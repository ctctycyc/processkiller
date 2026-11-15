from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import os
import subprocess
import uuid

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Render Cloud Injector is Running!"}

@app.post("/inject")
async def inject_apk(file: UploadFile = File(...)):
    os.system("rm -rf /tmp/work_*")
    temp_id = str(uuid.uuid4())[:8]
    work_dir = f"/tmp/work_{temp_id}"
    os.makedirs(work_dir, exist_ok=True)
    
    apk_path = f"{work_dir}/target.apk"
    with open(apk_path, "wb") as f:
        f.write(await file.read())
        
    try:
        res_d = subprocess.run(["java", "-jar", "apktool.jar", "d", apk_path, "-o", f"{work_dir}/unpacked", "-f"], capture_output=True, text=True)
        if res_d.returncode != 0:
            return JSONResponse(status_code=500, content={"error": "解包失败", "details": res_d.stderr})
        
        os.makedirs(f"{work_dir}/unpacked/assets", exist_ok=True)
        with open(f"{work_dir}/unpacked/assets/payload_test.txt", "w") as f:
            f.write("Injected by Render!")
            
        new_apk = f"{work_dir}/rebuilt.apk"
        res_b = subprocess.run(["java", "-jar", "apktool.jar", "b", f"{work_dir}/unpacked", "-o", new_apk], capture_output=True, text=True)
        if res_b.returncode != 0:
            return JSONResponse(status_code=500, content={"error": "打包失败", "details": res_b.stderr})
            
        res_s = subprocess.run(["java", "-jar", "signer.jar", "-a", new_apk, "--allowResign"], capture_output=True, text=True)
        if res_s.returncode != 0:
             return JSONResponse(status_code=500, content={"error": "签名失败", "details": res_s.stdout + res_s.stderr})
        
        signed_apk = f"{work_dir}/rebuilt-aligned-signed.apk"
        return FileResponse(signed_apk, media_type="application/vnd.android.package-archive", filename=f"injected_{temp_id}.apk")
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "系统错误", "details": str(e)})
