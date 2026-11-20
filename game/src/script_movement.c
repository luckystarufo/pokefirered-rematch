#include "global.h"
#include "task.h"
#include "util.h"
#include "event_object_movement.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"

static EWRAM_DATA const u8 (*sMovementScripts[OBJECT_EVENTS_COUNT]) = {};
// Rematch: which object each movement slot drives, and which slots have finished. Vanilla kept these in the
// task's data (object ids packed from data[1], a u16 "finished" mask in data[0]), which only fits 16 slots;
// OBJECT_EVENTS_COUNT is 40 now (the mask is two 32-bit words).
static EWRAM_DATA u8 sMoveObjEventIds[OBJECT_EVENTS_COUNT] = {0};
static EWRAM_DATA u32 sMoveScriptsFinished[(OBJECT_EVENTS_COUNT + 31) / 32] = {0};

static void ScriptMovement_StartMoveObjects(u8 priority);
static u8 GetMoveObjectsTaskId(void);
static u8 ScriptMovement_TryAddNewMovement(u8 taskId, u8 objEventId, const u8 *movementScript);
static u8 GetMovementScriptIdFromObjectEventId(u8 taskId, u8 objEventId);
static bool8 IsMovementScriptFinished(u8 taskId, u8 moveScrId);
static void ScriptMovement_MoveObjects(u8 taskId);
static void ScriptMovement_AddNewMovement(u8 taskId, u8 moveScrId, u8 objEventId, const u8 *movementScript);
static void ScriptMovement_UnfreezeActiveObjects(u8 taskId);
static void ScriptMovement_TakeStep(u8 taskId, u8 moveScrId, u8 objEventId, const u8 *movementScript);

bool8 ScriptMovement_StartObjectMovementScript(u8 localId, u8 mapNum, u8 mapGroup, const u8 *movementScript)
{
    u8 objEventId;
    if (TryGetObjectEventIdByLocalIdAndMap(localId, mapNum, mapGroup, &objEventId))
        return TRUE;

    if (!FuncIsActiveTask(ScriptMovement_MoveObjects))
        ScriptMovement_StartMoveObjects(50);
    return ScriptMovement_TryAddNewMovement(GetMoveObjectsTaskId(), objEventId, movementScript);
}

bool8 ScriptMovement_IsObjectMovementFinished(u8 localId, u8 mapNum, u8 mapGroup)
{
    u8 objEventId;
    u8 taskId;
    u8 moveScrId;
    if (TryGetObjectEventIdByLocalIdAndMap(localId, mapNum, mapGroup, &objEventId))
        return TRUE;
    taskId = GetMoveObjectsTaskId();
    moveScrId = GetMovementScriptIdFromObjectEventId(taskId, objEventId);
    if (moveScrId == OBJECT_EVENTS_COUNT)
        return TRUE;
    return IsMovementScriptFinished(taskId, moveScrId);
}

void ScriptMovement_UnfreezeObjectEvents(void)
{
    u8 taskId = GetMoveObjectsTaskId();
    if (taskId != TAIL_SENTINEL)
    {
        ScriptMovement_UnfreezeActiveObjects(taskId);
        DestroyTask(taskId);
    }
}

void ScriptMovement_StartMoveObjects(u8 priority)
{
    u8 i;
    CreateTask(ScriptMovement_MoveObjects, priority);
    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
        sMoveObjEventIds[i] = 0xFF;
    for (i = 0; i < ARRAY_COUNT(sMoveScriptsFinished); i++)
        sMoveScriptsFinished[i] = 0;
}

u8 GetMoveObjectsTaskId(void)
{
    return FindTaskIdByFunc(ScriptMovement_MoveObjects);
}

bool8 ScriptMovement_TryAddNewMovement(u8 taskId, u8 objEventId, const u8 *movementScript)
{
    u8 moveScrId;

    moveScrId = GetMovementScriptIdFromObjectEventId(taskId, objEventId);
    if (moveScrId != OBJECT_EVENTS_COUNT)
    {
        if (IsMovementScriptFinished(taskId, moveScrId) == FALSE)
        {
            return TRUE;
        }
        else
        {
            ScriptMovement_AddNewMovement(taskId, moveScrId, objEventId, movementScript);
            return FALSE;
        }
    }
    moveScrId = GetMovementScriptIdFromObjectEventId(taskId, LOCALID_PLAYER);
    if (moveScrId == OBJECT_EVENTS_COUNT)
    {
        return TRUE;
    }
    else
    {
        ScriptMovement_AddNewMovement(taskId, moveScrId, objEventId, movementScript);
        return FALSE;
    }
}

u8 GetMovementScriptIdFromObjectEventId(u8 taskId, u8 objEventId)
{
    u8 i;
    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
    {
        if (sMoveObjEventIds[i] == objEventId)
            return i;
    }
    return OBJECT_EVENTS_COUNT;
}

void LoadObjectEventIdPtrFromMovementScript(u8 taskId, u8 moveScrId, u8 **pObjEventId)
{
    *pObjEventId = &sMoveObjEventIds[moveScrId];
}

void SetObjectEventIdAtMovementScript(u8 taskId, u8 moveScrId, u8 objEventId)
{
    u8 *ptr;

    LoadObjectEventIdPtrFromMovementScript(taskId, moveScrId, &ptr);
    *ptr = objEventId;
}

void LoadObjectEventIdFromMovementScript(u8 taskId, u8 moveScrId, u8 *objEventId)
{
    u8 *ptr;

    LoadObjectEventIdPtrFromMovementScript(taskId, moveScrId, &ptr);
    *objEventId = *ptr;
}


static void ClearMovementScriptFinished(u8 taskId, u8 moveScrId)
{
    sMoveScriptsFinished[moveScrId / 32] &= ~(1u << (moveScrId % 32));
}

static void SetMovementScriptFinished(u8 taskId, u8 moveScrId)
{
    sMoveScriptsFinished[moveScrId / 32] |= 1u << (moveScrId % 32);
}

static bool8 IsMovementScriptFinished(u8 taskId, u8 moveScrId)
{
    if (sMoveScriptsFinished[moveScrId / 32] & (1u << (moveScrId % 32)))
        return TRUE;
    else
        return FALSE;
}

static void SetMovementScript(u8 moveScrId, const u8 *movementScript)
{
    sMovementScripts[moveScrId] = movementScript;
}

static const u8 *GetMovementScript(u8 moveScrId)
{
    return sMovementScripts[moveScrId];
}

static void ScriptMovement_AddNewMovement(u8 taskId, u8 moveScrId, u8 objEventId, const u8 *movementScript)
{
    ClearMovementScriptFinished(taskId, moveScrId);
    SetMovementScript(moveScrId, movementScript);
    SetObjectEventIdAtMovementScript(taskId, moveScrId, objEventId);
}

static void ScriptMovement_UnfreezeActiveObjects(u8 taskId)
{
    u8 *pObjEventId;
    u8 i;

    pObjEventId = sMoveObjEventIds;
    for (i = 0; i < OBJECT_EVENTS_COUNT; i++, pObjEventId++)
    {
        if (*pObjEventId != 0xFF)
            UnfreezeObjectEvent(&gObjectEvents[*pObjEventId]);
    }
}

static void ScriptMovement_MoveObjects(u8 taskId)
{
    u8 i;
    u8 objEventId;

    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
    {
        LoadObjectEventIdFromMovementScript(taskId, i, &objEventId);
        if (objEventId != 0xFF)
            ScriptMovement_TakeStep(taskId, i, objEventId, GetMovementScript(i));
    }
}

static void ScriptMovement_TakeStep(u8 taskId, u8 moveScrId, u8 objEventId, const u8 *movementScript)
{
    u8 nextMoveActionId;

    if (IsMovementScriptFinished(taskId, moveScrId) == TRUE)
        return;
    if (ObjectEventIsHeldMovementActive(&gObjectEvents[objEventId])
        && !ObjectEventClearHeldMovementIfFinished(&gObjectEvents[objEventId]))
        return;

    nextMoveActionId = *movementScript;
    if (nextMoveActionId == MOVEMENT_ACTION_STEP_END)
    {
        SetMovementScriptFinished(taskId, moveScrId);
        FreezeObjectEvent(&gObjectEvents[objEventId]);
    }
    else
    {
        if (!ObjectEventSetHeldMovement(&gObjectEvents[objEventId], nextMoveActionId))
        {
            movementScript++;
            SetMovementScript(moveScrId, movementScript);
        }
    }
}
