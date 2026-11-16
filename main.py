
import asyncio
import io
import secrets
import socket
import time
from pathlib import Path

import qrcode
from aiohttp import web

PORT = 8000
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ROOM_TTL = 3600

rooms = {}


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#090d1b">
<title>FileDrop — Share instantly</title>

<style>
*{box-sizing:border-box}

body{
 margin:0;
 background:#090d1b;
 color:#f4f6ff;
 font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
 min-height:100vh;
}

header{
 padding:24px 7%;
 display:flex;
 justify-content:space-between;
 align-items:center;
 border-bottom:1px solid #202840;
}

.logo{
 font-size:25px;
 font-weight:850;
 letter-spacing:-1px;
}

.logo span{color:#8192ff}

.tag{
 font-size:12px;
 color:#a8b1ca;
 border:1px solid #303b58;
 padding:8px 13px;
 border-radius:30px;
}

main{
 max-width:760px;
 margin:65px auto;
 padding:0 22px;
 text-align:center;
}

h1{
 font-size:clamp(38px,7vw,60px);
 letter-spacing:-3px;
 margin:0 0 15px;
}

h1 span{
 background:linear-gradient(90deg,#8192ff,#c18aff);
 -webkit-background-clip:text;
 background-clip:text;
 color:transparent;
}

.subtitle{
 color:#9ba8c4;
 font-size:16px;
 line-height:1.7;
}

.card{
 margin:35px auto;
 background:#11182b;
 border:1px solid #283451;
 border-radius:23px;
 padding:30px;
 max-width:560px;
 text-align:left;
}

.tabs{
 display:flex;
 gap:10px;
 margin-bottom:25px;
}

button{
 cursor:pointer;
 border:0;
 font-weight:700;
 font-size:14px;
 border-radius:12px;
 padding:14px 20px;
 transition:.2s;
}

button:hover{
 filter:brightness(1.15);
 transform:translateY(-1px);
}

.tab{
 flex:1;
 background:#1b2540;
 color:#aeb9d5;
}

.tab.active{
 background:#303e70;
 color:white;
}

.primary{
 background:linear-gradient(110deg,#647cff,#9872ff);
 color:white;
 width:100%;
 margin-top:15px;
}

.secondary{
 background:#25314f;
 color:white;
 width:100%;
 margin-top:10px;
}

input{
 width:100%;
 background:#0b1222;
 border:1px solid #34415e;
 border-radius:12px;
 padding:15px;
 color:white;
 font-size:15px;
 margin-top:10px;
 outline:none;
}

input:focus{
 border-color:#8192ff;
}

label{
 font-size:13px;
 color:#aeb9d5;
}

.drop{
 border:2px dashed #485783;
 background:#0c1428;
 border-radius:17px;
 padding:35px 15px;
 text-align:center;
 margin-top:18px;
 transition:.2s;
}

.drop.dragover{
 background:#1c2850;
 border-color:#899aff;
}

.drop strong{
 display:block;
 font-size:17px;
 margin-bottom:8px;
}

.drop p{
 color:#99a7c5;
 font-size:13px;
}

#status{
 margin-top:20px;
 color:#aeb9d5;
 font-size:13px;
 line-height:1.6;
 text-align:center;
}

#qr{
 width:160px;
 height:160px;
 background:white;
 padding:8px;
 border-radius:12px;
 margin:18px auto;
 display:block;
}

.code{
 font-size:35px;
 letter-spacing:7px;
 text-align:center;
 font-weight:850;
 color:#a5b4ff;
 margin:18px;
}

.progress{
 height:8px;
 background:#25304b;
 border-radius:20px;
 overflow:hidden;
 margin-top:18px;
}

#progressBar{
 height:100%;
 width:0%;
 background:linear-gradient(90deg,#647cff,#c18aff);
 transition:width .2s;
}

.file-item{
 display:flex;
 align-items:center;
 justify-content:space-between;
 gap:12px;
 padding:14px;
 background:#0b1222;
 border-radius:12px;
 margin-top:10px;
 font-size:13px;
}

.file-item a{
 color:#a5b4ff;
 text-decoration:none;
 font-weight:700;
}

.small{
 color:#8290af;
 font-size:12px;
}

.hidden{display:none!important}

footer{
 text-align:center;
 color:#66728e;
 font-size:12px;
 padding:30px;
}

@media(max-width:500px){
 main{margin:40px auto}
 .card{padding:20px}
 header{padding:20px}
}
</style>
</head>

<body>

<header>
 <div class="logo">File<span>Drop</span></div>
 <div class="tag">FREE & OPEN SOURCE</div>
</header>

<main>

<h1>Share files.<br><span>Instantly.</span></h1>

<p class="subtitle">
Send files between your devices.<br>
No account. No complicated setup.
</p>

<div class="card">

<div class="tabs">
 <button class="tab active" id="sendTab" onclick="showTab('send')">
 Send files
 </button>
 <button class="tab" id="receiveTab" onclick="showTab('receive')">
 Receive files
 </button>
</div>

<!-- SEND PANEL -->

<section id="sendPanel">

<label>Select files to share</label>

<div class="drop" id="dropZone">
 <div style="font-size:35px">📁</div>
 <strong>Drop your files here</strong>
 <p>or click the button below to browse</p>
 <input type="file" id="fileInput" multiple hidden>
 <button class="secondary" onclick="document.getElementById('fileInput').click()">
 Browse files
 </button>
</div>

<div id="selectedFiles" class="small" style="margin-top:15px"></div>

<button class="primary" id="createBtn" onclick="createRoom()">
 Create transfer
</button>

<div id="senderResult" class="hidden">

 <div style="text-align:center;margin-top:25px">
  <p class="small">YOUR TRANSFER CODE</p>
  <div class="code" id="roomCode"></div>
  <img id="qr" alt="Transfer QR code">
  <p class="small">Scan this QR code with another device.</p>
  <button class="secondary" onclick="copyLink()">Copy sharing link</button>
 </div>

 <div class="progress">
  <div id="progressBar"></div>
 </div>

 <div id="uploadStatus" class="small" style="text-align:center;margin-top:12px">
  Waiting for files...
 </div>

</div>

</section>

<!-- RECEIVE PANEL -->

<section id="receivePanel" class="hidden">

<label>Enter your transfer code</label>

<input id="joinCode" placeholder="e.g. A1B2C3" maxlength="6">

<button class="primary" onclick="joinRoom()">
 Join transfer
</button>

<div id="receiverResult" class="hidden">

 <p class="small" style="margin-top:25px">
  CONNECTED TO TRANSFER
 </p>

 <div class="code" id="receiverCode"></div>

 <div id="receivedFiles"></div>

 <p class="small" id="receiverStatus">
  Waiting for files...
 </p>

</div>

</section>

<div id="status"></div>

</div>

<p class="subtitle" style="font-size:13px">
Simple. Private. Open source.
</p>

</main>

<footer>
FileDrop · Free file sharing · No account required
</footer>

<script>
let selectedFiles = [];
let currentRoom = null;
let polling = false;
let knownFiles = new Set();

const $ = id => document.getElementById(id);

function showTab(tab){
 $('sendPanel').classList.toggle('hidden',tab!=='send');
 $('receivePanel').classList.toggle('hidden',tab!=='receive');
 $('sendTab').classList.toggle('active',tab==='send');
 $('receiveTab').classList.toggle('active',tab==='receive');
 $('status').textContent='';
}

function formatSize(bytes){
 if(bytes < 1024) return bytes+' B';
 if(bytes < 1024*1024) return (bytes/1024).toFixed(1)+' KB';
 return (bytes/1024/1024).toFixed(2)+' MB';
}

function updateSelected(){
 $('selectedFiles').textContent =
 selectedFiles.map(f=>f.name+' ('+formatSize(f.size)+')').join(' · ');
}

$('fileInput').addEventListener('change',e=>{
 selectedFiles=Array.from(e.target.files);
 updateSelected();
});

const drop=$('dropZone');

drop.addEventListener('dragover',e=>{
 e.preventDefault();
 drop.classList.add('dragover');
});

drop.addEventListener('dragleave',()=>{
 drop.classList.remove('dragover');
});

drop.addEventListener('drop',e=>{
 e.preventDefault();
 drop.classList.remove('dragover');
 selectedFiles=Array.from(e.dataTransfer.files);
 updateSelected();
});

async function createRoom(){
 if(!selectedFiles.length){
  $('status').textContent='Please select at least one file.';
  return;
 }

 if(selectedFiles.some(f=>f.size>100*1024*1024)){
  $('status').textContent='Each file must be smaller than 100 MB.';
  return;
 }

 $('createBtn').disabled=true;
 $('status').textContent='Creating your transfer...';

 try{
  const response=await fetch('/api/rooms',{
   method:'POST'
  });

  const data=await response.json();

  if(!response.ok) throw new Error(data.error);

  currentRoom=data.code;

  $('roomCode').textContent=currentRoom;
  $('qr').src='/qr/'+currentRoom;
  $('senderResult').classList.remove('hidden');
  $('status').textContent='Your transfer is ready.';

  uploadFiles();

 }catch(e){
  $('status').textContent=e.message;
  $('createBtn').disabled=false;
 }
}

async function uploadFiles(){
 let total=selectedFiles.reduce((s,f)=>s+f.size,0);
 let completed=0;

 for(const file of selectedFiles){
  const form=new FormData();
  form.append('file',file);

  try{
   const response=await fetch('/api/rooms/'+currentRoom+'/upload',{
    method:'POST',
    body:form
   });

   const data=await response.json();

   if(!response.ok) throw new Error(data.error);

   completed+=file.size;

   $('progressBar').style.width=
    (total ? completed/total*100 : 100)+'%';

   $('uploadStatus').textContent=
    'Uploaded '+file.name+' · '+formatSize(completed)+' / '+formatSize(total);

  }catch(e){
   $('uploadStatus').textContent='Upload failed: '+e.message;
   return;
  }
 }

 $('uploadStatus').textContent='All files uploaded successfully!';
}

async function copyLink(){
 const link=location.origin+'/?room='+currentRoom;
 try{
  await navigator.clipboard.writeText(link);
  $('status').textContent='Sharing link copied!';
 }catch(e){
  $('status').textContent='Copy failed. Share your room code instead.';
 }
}

async function joinRoom(){
 const code=$('joinCode').value.trim().toUpperCase();

 if(!/^[A-F0-9]{6}$/.test(code)){
  $('status').textContent='Please enter a valid 6-character code.';
  return;
 }

 try{
  const response=await fetch('/api/rooms/'+code);
  const data=await response.json();

  if(!response.ok) throw new Error(data.error);

  currentRoom=code;
  $('receiverCode').textContent=code;
  $('receiverResult').classList.remove('hidden');
  $('status').textContent='Successfully joined the transfer.';

  if(!polling){
   polling=true;
   pollFiles();
  }

 }catch(e){
  $('status').textContent=e.message;
 }
}

async function pollFiles(){
 while(currentRoom && polling){
  try{
   const response=await fetch('/api/rooms/'+currentRoom+'/files');
   const data=await response.json();

   if(!response.ok) throw new Error(data.error);

   for(const file of data.files){
    if(knownFiles.has(file.id)) continue;

    knownFiles.add(file.id);

    const item=document.createElement('div');
    item.className='file-item';

    const name=document.createElement('span');
    name.textContent=file.name+' ('+formatSize(file.size)+')';

    const link=document.createElement('a');
    link.textContent='Download';
    link.href='/api/rooms/'+currentRoom+'/download/'+file.id;
    link.download=file.name;

    item.append(name,link);
    $('receivedFiles').appendChild(item);
   }

   $('receiverStatus').textContent=
    data.files.length ? 'Files are ready to download.' : 'Waiting for files...';

  }catch(e){
   $('receiverStatus').textContent=e.message;
   polling=false;
   break;
  }

  await new Promise(resolve=>setTimeout(resolve,2000));
 }
}

const params=new URLSearchParams(location.search);
const initialRoom=params.get('room');

if(initialRoom){
 showTab('receive');
 $('joinCode').value=initialRoom.toUpperCase();
 joinRoom();
}
</script>

</body>
</html>
"""


def clean_filename(name):
    name = Path(name).name
    name = re.sub(r'[\x00-\x1f]', '', name)
    return name[:200] or "download"


def cleanup_rooms():
    now = time.time()
    expired = [
        code for code, room in rooms.items()
        if now - room["created"] > ROOM_TTL
    ]
    for code in expired:
        del rooms[code]


async def homepage(request):
    return web.Response(text=HTML, content_type="text/html")


async def create_room(request):
    cleanup_rooms()

    code = secrets.token_hex(3).upper()

    rooms[code] = {
        "created": time.time(),
        "files": {}
    }

    return web.json_response({"code": code})


async def check_room(request):
    cleanup_rooms()

    code = request.match_info["code"].upper()

    if code not in rooms:
        return web.json_response(
            {"error": "Transfer not found or expired."},
            status=404
        )

    return web.json_response({"success": True})


async def upload_file(request):
    cleanup_rooms()

    code = request.match_info["code"].upper()

    if code not in rooms:
        return web.json_response(
            {"error": "Transfer not found."},
            status=404
        )

    try:
        reader = await request.multipart()
        field = await reader.next()

        if field is None or field.name != "file":
            return web.json_response(
                {"error": "No file received."},
                status=400
            )

        filename = clean_filename(field.filename or "download")
        content = bytearray()

        while True:
            chunk = await field.read_chunk(size=1024 * 1024)

            if not chunk:
                break

            content.extend(chunk)

            if len(content) > MAX_FILE_SIZE:
                return web.json_response(
                    {"error": "File exceeds the 100 MB limit."},
                    status=413
                )

        file_id = secrets.token_urlsafe(12)

        rooms[code]["files"][file_id] = {
            "name": filename,
            "content": bytes(content),
            "size": len(content)
        }

        return web.json_response({
            "success": True,
            "id": file_id
        })

    except Exception:
        return web.json_response(
            {"error": "Upload failed."},
            status=500
        )


async def list_files(request):
    cleanup_rooms()

    code = request.match_info["code"].upper()

    if code not in rooms:
        return web.json_response(
            {"error": "Transfer not found or expired."},
            status=404
        )

    files = []

    for file_id, file in rooms[code]["files"].items():
        files.append({
            "id": file_id,
            "name": file["name"],
            "size": file["size"]
        })

    return web.json_response({"files": files})


async def download_file(request):
    cleanup_rooms()

    code = request.match_info["code"].upper()
    file_id = request.match_info["file_id"]

    if code not in rooms:
        return web.json_response(
            {"error": "Transfer not found."},
            status=404
        )

    file = rooms[code]["files"].get(file_id)

    if not file:
        return web.json_response(
            {"error": "File not found."},
            status=404
        )

    response = web.Response(
        body=file["content"],
        content_type="application/octet-stream"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename*=UTF-8''" +
        __import__("urllib.parse").parse.quote(file["name"])
    )

    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


async def generate_qr(request):
    code = request.match_info["code"].upper()

    if code not in rooms:
        raise web.HTTPNotFound()

    ip = get_local_ip()
    url = f"http://{ip}:{PORT}/?room={code}"

    qr = qrcode.make(url)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return web.Response(
        body=buffer.getvalue(),
        content_type="image/png"
    )


def create_app():
    app = web.Application(
        client_max_size=MAX_FILE_SIZE + 1024 * 1024
    )

    app.router.add_get("/", homepage)
    app.router.add_post("/api/rooms", create_room)
    app.router.add_get("/api/rooms/{code}", check_room)
    app.router.add_post("/api/rooms/{code}/upload", upload_file)
    app.router.add_get("/api/rooms/{code}/files", list_files)
    app.router.add_get(
        "/api/rooms/{code}/download/{file_id}",
        download_file
    )
    app.router.add_get("/qr/{code}", generate_qr)

    return app


if __name__ == "__main__":
    print("\n===================================")
    print("          FILEDROP")
    print("===================================")
    print(f"Local: http://localhost:{PORT}")
    print(f"Network: http://{get_local_ip()}:{PORT}")
    print("Press CTRL+C to stop the server.")
    print("===================================\n")

    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=PORT
    )
