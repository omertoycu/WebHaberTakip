import uvicorn
import sys
import os

# Backend dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("=" * 60)
    print("  Kocaeli Haber İzleme Sistemi")
    print("  Backend API: http://localhost:8000")
    print("  Swagger UI:  http://localhost:8000/docs")
    print("  Frontend:    http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
        log_level="info"
    )
