/* Playback only: compilation and inspection happen in Python. */
'use strict';
const $=id=>document.getElementById(id);
let device='cyberboard',frame=0,playing=!matchMedia('(prefers-reduced-motion: reduce)').matches,last=0,photoPreview=null,photoUrl=null,photoGeneration=0;
function current(){return window.LUMEN_EXAMPLES[device];}
function matrix(){
 const d=current().design,ctx=$('pixels').getContext('2d'),w=d.device.top_width,h=d.device.top_height;
 ctx.clearRect(0,0,960,480);const size=Math.min(920/w,440/h),ox=(960-w*size)/2,oy=(480-h*size)/2;
 d.frames[frame].forEach((rgb,i)=>{ctx.fillStyle=rgb;ctx.fillRect(ox+(i%w)*size+1,oy+Math.floor(i/w)*size+1,Math.max(1,size-2),Math.max(1,size-2));});
 const keys=$('keys').getContext('2d');keys.clearRect(0,0,960,180);
 d.device.key_coordinates.forEach((p,i)=>{if(!p)return;keys.fillStyle=d.keyframes[frame][i];keys.beginPath();keys.arc(25+p[0]*910,20+p[1]*140,device==='matrix16'?12:7,0,Math.PI*2);keys.fill();});
 $('frame').value=frame;$('position').textContent=`${frame+1} / ${d.frame_count}`;
 if(photoPreview)photoPreview.seek(frame);
}
function select(){
 device=$('device').value;frame=0;last=0;const {design,report}=current();$('frame').max=design.frame_count-1;
 $('quality').textContent=report.passed?'PASS · compiled pixels passed checks':'Needs attention';
 $('report').textContent=JSON.stringify({issues:report.issues,warnings:report.warnings,regions:report.metrics.regions},null,2);
 $('photo-section').hidden=device!=='cyberboard';if(photoPreview)photoPreview.setVisible(device==='cyberboard');matrix();
}
$('device').addEventListener('change',select);
$('play').textContent=playing?'Pause':'Play';
$('play').addEventListener('click',()=>{playing=!playing;last=0;$('play').textContent=playing?'Pause':'Play';});
$('frame').addEventListener('input',()=>{frame=Number($('frame').value);last=0;matrix();});
$('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(current().design,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`${device}.design.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('photo').addEventListener('change',async()=>{
 const generation=++photoGeneration,file=$('photo').files[0];if(!file)return;
 if(file.size>20*1024*1024){$('photo-status').textContent='Photo exceeds 20 MiB.';return;}
 const url=URL.createObjectURL(file),image=new Image();
 try{image.src=url;await image.decode();if(generation!==photoGeneration){URL.revokeObjectURL(url);return;}
 if(image.naturalWidth!==1619||image.naturalHeight!==1080)throw Error('Expected the calibrated 1619 × 1080 reference photo.');
 if(photoPreview)photoPreview.destroy();if(photoUrl)URL.revokeObjectURL(photoUrl);photoUrl=url;
 const view={...LUMEN_EXAMPLES.photoCalibration,image:url};
 photoPreview=new KeyboardPreview($('photo-preview'),{views:{front:view},view:'front',design:LUMEN_EXAMPLES.cyberboard.design,visible:device==='cyberboard',onError:()=>{$('photo-status').textContent='Photo preview could not render.';}});
 photoPreview.pause();photoPreview.seek(frame);$('photo-status').textContent='Local photo loaded · calibrated overlay · no upload';
 }catch(error){URL.revokeObjectURL(url);$('photo-status').textContent=error.message;}
});
function animate(time){if(playing&&!document.hidden){if(!last)last=time;const elapsed=time-last,ms=current().design.speed_ms;if(elapsed>=ms){const steps=Math.floor(elapsed/ms);frame=(frame+steps)%current().design.frame_count;last+=steps*ms;matrix();}}else last=0;requestAnimationFrame(animate);}
document.addEventListener('visibilitychange',()=>{last=0;if(photoPreview)photoPreview.setVisible(!document.hidden&&device==='cyberboard');});
window.addEventListener('pagehide',()=>{photoGeneration++;if(photoPreview)photoPreview.destroy();if(photoUrl)URL.revokeObjectURL(photoUrl);});
select();requestAnimationFrame(animate);
