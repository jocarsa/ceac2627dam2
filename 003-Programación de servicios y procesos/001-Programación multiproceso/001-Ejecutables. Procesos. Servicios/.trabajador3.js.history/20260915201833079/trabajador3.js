onmessage = function(){
	let numero = 1.00000000543;
  for(i = 0;i<1000000000000;i++){
    numero *= 1.00000000543;
  }
  console.log("acabado")
  postMessage("ok volvemos")
}