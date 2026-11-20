// The CDK app. Settings come from .local/deploy.json (git-ignored): the notification email and the two
// secrets. The ROM to upload is prepared in .local/rom-upload/ by tools/deploy.sh.
import * as fs from 'fs';
import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import { RematchStack } from '../lib/rematch-stack';

const root = path.join(__dirname, '..', '..');
const configPath = path.join(root, '.local', 'deploy.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
for (const key of ['notifyEmail', 'sessionSecret', 'originSecret']) {
  if (!config[key]) throw new Error(`${configPath}: missing "${key}"`);
}
const romDir = path.join(root, '.local', 'rom-upload');
if (!fs.existsSync(path.join(romDir, 'pokefirered.gba'))) {
  throw new Error(`No ROM in ${romDir}: run tools/deploy.sh (it builds this folder) instead of cdk directly.`);
}

const app = new cdk.App();
new RematchStack(app, 'Rematch', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'us-east-1' },
  description: 'Rematch: a private FireRed reunion page (CloudFront + S3 + Lambda + DynamoDB + SNS)',
  notifyEmail: config.notifyEmail,
  sessionSecret: config.sessionSecret,
  originSecret: config.originSecret,
  webDir: path.join(root, 'web'),
  romDir,
});
