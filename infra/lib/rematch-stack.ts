// Everything the Rematch page needs on AWS, in one stack (one stack avoids the cross-stack cycle that an
// S3 bucket + CloudFront Origin Access Control otherwise creates).
//
//   CloudFront (HTTPS) ── /              → S3, private (page, scripts, styles, font)       public
//                      ├─ /emulator/*    → S3, private (EmulatorJS)                         session cookie
//                      ├─ /rom/*         → S3, private (the ROM, gzipped, + manifest)       session cookie
//                      └─ /api/*         → Lambda (invites, messages, invitation requests)
//                                             ├─ DynamoDB: invites, messages, requests, throttle
//                                             └─ SNS → email to the host
import * as fs from 'fs';
import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as budgets from 'aws-cdk-lib/aws-budgets';

export interface RematchStackProps extends cdk.StackProps {
  notifyEmail: string;
  sessionSecret: string; // signs session cookies (Lambda) and checks them (CloudFront Function)
  originSecret: string;  // CloudFront → Lambda header, so the API only answers via CloudFront
  webDir: string;        // web/ (the page, EmulatorJS, font)
  romDir: string;        // the gzipped ROM + manifest, prepared by tools/deploy.sh
}

export class RematchStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: RematchStackProps) {
    super(scope, id, props);

    // --- Storage ------------------------------------------------------------------------------------
    const bucket = new s3.Bucket(this, 'Site', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const table = (name: string, key: string, keep: boolean, ttl?: string) =>
      new dynamodb.TableV2(this, name, {
        partitionKey: { name: key, type: dynamodb.AttributeType.STRING },
        billing: dynamodb.Billing.onDemand(),
        timeToLiveAttribute: ttl,
        // friends' words outlive a teardown; the rest goes with the stack
        removalPolicy: keep ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      });
    const invites = table('Invites', 'code', false);
    const messages = table('Messages', 'id', true);
    const requests = table('InviteRequests', 'id', true);
    const throttle = table('Throttle', 'key', false, 'expiresAt');

    const topic = new sns.Topic(this, 'Notify', { displayName: 'Rematch' });
    topic.addSubscription(new subs.EmailSubscription(props.notifyEmail));

    // --- The API --------------------------------------------------------------------------------------
    const api = new lambda.Function(this, 'Api', {
      runtime: lambda.Runtime.NODEJS_22_X,
      architecture: lambda.Architecture.ARM_64,
      code: lambda.Code.fromAsset(path.join(__dirname, '..', 'lambda')),
      handler: 'api.handler',
      memorySize: 256,
      timeout: cdk.Duration.seconds(10),
      // at most 10 copies at once: a flood of requests queues up (and gets 429s) instead of scaling the bill
      reservedConcurrentExecutions: 10,
      logGroup: new logs.LogGroup(this, 'ApiLogs', {
        retention: logs.RetentionDays.ONE_MONTH,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
      }),
      environment: {
        INVITES_TABLE: invites.tableName,
        MESSAGES_TABLE: messages.tableName,
        REQUESTS_TABLE: requests.tableName,
        THROTTLE_TABLE: throttle.tableName,
        TOPIC_ARN: topic.topicArn,
        SESSION_SECRET: props.sessionSecret,
        ORIGIN_SECRET: props.originSecret,
      },
    });
    // exactly the calls api.mjs makes, nothing more (no scans, no deletes)
    const allow = (actions: string[], resource: string) =>
      api.addToRolePolicy(new iam.PolicyStatement({ actions, resources: [resource] }));
    allow(['dynamodb:GetItem', 'dynamodb:UpdateItem'], invites.tableArn);
    allow(['dynamodb:PutItem'], messages.tableArn);
    allow(['dynamodb:PutItem'], requests.tableArn);
    allow(['dynamodb:UpdateItem'], throttle.tableArn);
    allow(['sns:Publish'], topic.topicArn);
    // AWS_IAM: only requests signed by our CloudFront distribution (Origin Access Control) reach the code;
    // anything else is refused by AWS before the function runs (and before it costs anything)
    const apiUrl = api.addFunctionUrl({ authType: lambda.FunctionUrlAuthType.AWS_IAM });

    // --- The gate at the edge ---------------------------------------------------------------------------
    const revoked = new cloudfront.KeyValueStore(this, 'Revoked', {
      comment: 'Rematch: revoked invite codes (revoked:<CODE>)',
    });
    const checkSource = fs.readFileSync(path.join(__dirname, '..', 'edge', 'session-check.js'), 'utf8')
      .replace('__SESSION_SECRET__', props.sessionSecret)
      .replace('__KVS_ID__', revoked.keyValueStoreId);
    const sessionCheck = new cloudfront.Function(this, 'SessionCheck', {
      code: cloudfront.FunctionCode.fromInline(checkSource),
      runtime: cloudfront.FunctionRuntime.JS_2_0,
      keyValueStore: revoked,
      comment: 'Rematch: only friends with a live invite get the emulator and the ROM',
    });

    // --- CloudFront --------------------------------------------------------------------------------------
    const siteOrigin = origins.S3BucketOrigin.withOriginAccessControl(bucket);
    const gated: cloudfront.BehaviorOptions = {
      origin: siteOrigin,
      viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      compress: true,
      functionAssociations: [{ function: sessionCheck, eventType: cloudfront.FunctionEventType.VIEWER_REQUEST }],
    };
    const distribution = new cloudfront.Distribution(this, 'Cdn', {
      comment: 'Rematch',
      defaultRootObject: 'index.html',
      priceClass: cloudfront.PriceClass.PRICE_CLASS_ALL, // friends may be anywhere
      httpVersion: cloudfront.HttpVersion.HTTP2_AND_3,
      defaultBehavior: {
        origin: siteOrigin,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        responseHeadersPolicy: cloudfront.ResponseHeadersPolicy.SECURITY_HEADERS,
        compress: true,
      },
      additionalBehaviors: {
        'emulator/*': gated,
        'rom/*': gated,
        'api/*': {
          origin: origins.FunctionUrlOrigin.withOriginAccessControl(apiUrl, {
            customHeaders: { 'x-origin-verify': props.originSecret }, // second lock, checked in api.mjs
          }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy: new cloudfront.OriginRequestPolicy(this, 'ApiForwarding', {
            // (the page's x-amz-content-sha256 body hash goes through on its own: CloudFront uses it to sign)
            comment: 'Rematch API: the session cookie and the real visitor address',
            cookieBehavior: cloudfront.OriginRequestCookieBehavior.allowList('rematch_session'),
            headerBehavior: cloudfront.OriginRequestHeaderBehavior.allowList('content-type', 'CloudFront-Viewer-Address'),
            queryStringBehavior: cloudfront.OriginRequestQueryStringBehavior.none(),
          }),
        },
      },
    });

    // --- A spending alarm --------------------------------------------------------------------------------
    // Emails the host when this month's AWS bill passes $5 (or is forecast to). Budgets are free.
    new budgets.CfnBudget(this, 'SpendAlarm', {
      budget: { budgetType: 'COST', timeUnit: 'MONTHLY', budgetLimit: { amount: 5, unit: 'USD' } },
      notificationsWithSubscribers: (['ACTUAL', 'FORECASTED'] as const).map((notificationType) => ({
        notification: { notificationType, comparisonOperator: 'GREATER_THAN', threshold: 100, thresholdType: 'PERCENTAGE' },
        subscribers: [{ subscriptionType: 'EMAIL', address: props.notifyEmail }],
      })),
    });

    // --- Upload the page and the ROM -----------------------------------------------------------------------
    new s3deploy.BucketDeployment(this, 'DeploySite', {
      sources: [s3deploy.Source.asset(props.webDir, { exclude: ['rom', 'rom/**', '*.sh', '.DS_Store'] })],
      destinationBucket: bucket,
      exclude: ['rom/*'], // leave the ROM (its own deployment, below) alone when pruning
      distribution,
      distributionPaths: ['/*'],
      memoryLimit: 1024,
    });
    new s3deploy.BucketDeployment(this, 'DeployRom', {
      sources: [s3deploy.Source.asset(props.romDir)],
      destinationBucket: bucket,
      destinationKeyPrefix: 'rom/',
      contentEncoding: 'gzip', // pre-compressed by tools/deploy.sh: 16 MB → ~5 MB on the wire
      distribution,
      distributionPaths: ['/rom/*'],
      memoryLimit: 1024,
    });

    // --- What the scripts need ------------------------------------------------------------------------------
    new cdk.CfnOutput(this, 'SiteUrl', { value: `https://${distribution.distributionDomainName}/` });
    new cdk.CfnOutput(this, 'InvitesTable', { value: invites.tableName });
    new cdk.CfnOutput(this, 'MessagesTable', { value: messages.tableName });
    new cdk.CfnOutput(this, 'RequestsTable', { value: requests.tableName });
    new cdk.CfnOutput(this, 'RevokedStoreArn', { value: revoked.keyValueStoreArn });
  }
}
