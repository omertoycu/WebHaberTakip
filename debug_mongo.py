import asyncio
import sys
import traceback

sys.path.insert(0, '.')

async def test():
    from backend.config import MONGODB_URI, DB_NAME
    print(f"URI (repr): {repr(MONGODB_URI)}")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[DB_NAME]
        # Simple ping command
        result = await client.admin.command('ping')
        print(f"Ping OK: {result}")
        client.close()
    except Exception as e:
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR MSG: {str(e)}")
        traceback.print_exc()

asyncio.run(test())
