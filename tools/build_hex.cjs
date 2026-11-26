// npm install in tools; node tools/build_hex.cjs <official-V2-runtime.hex>
const fs=require('fs'), path=require('path');
const {MicropythonFsHex}=require('@microbit/microbit-fs');
const root=path.resolve(__dirname,'..');
if(!process.argv[2])throw Error('Pass official micro:bit V2 MicroPython runtime HEX path');
const runtime=fs.readFileSync(process.argv[2],'utf8');
function build(name,files){const img=new MicropythonFsHex(runtime);for(const [target,source] of Object.entries(files))img.write(target,fs.readFileSync(path.join(root,source),'utf8'));fs.writeFileSync(path.join(root,name),img.getIntelHex());console.log(name);}
build('receiver/receiver.hex',{'main.py':'receiver/main.py','decoder.py':'receiver/decoder.py'});
build('examples/starter_python.hex',{'main.py':'examples/starter_python.py'});
