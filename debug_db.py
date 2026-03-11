import asyncio
import sys
import traceback

sys.path.insert(0, '.')

async def test():
    from backend.database import init_db
    try:
        await init_db()
        print('DB OK')
    except Exception as e:
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR MSG: {str(e)[:500]}")
        traceback.print_exc()

asyncio.run(test())
