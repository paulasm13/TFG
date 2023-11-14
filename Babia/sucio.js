AFRAME.registerComponent('env5',{
	init:function(){
		let el = this.el;
		el.addEventListener('grab-start', function () {
			env = document.getElementById('env')

			if (env) {
				env.remove()
			}
				env = document.createElement('a-entity')
				env.setAttribute('environment',"preset:default")
				env.setAttribute('id',"env")
				let scene = document.querySelector('#scn');
				console.log(scene)
				scene.appendChild(env);

		});
		el.addEventListener('raycaster-intersected', function () {
			el.setAttribute('material',"color:#adadad; opacity: 0.5");
		});
		el.addEventListener('raycaster-intersected-cleared', function () {
			el.setAttribute('material',"color:white; opacity: 0.25");
		});
	}
});

AFRAME.registerComponent('selectenv',{
	init:function(){
		let el = this.el;
		let show = false;
		el.addEventListener('grab-start', function () {
		//tip = document.getElementById('tip');
		if (show === false){
			show = true;
			console.log("Abierto menú")
			let env1 = document.createElement('a-box');
			env1.setAttribute('position',{x:0,y:0.1,z:0});
			env1.setAttribute('rotation',{x:0,y:-25,z:0});
			env1.setAttribute('id','env1');
			env1.setAttribute('class','remote');
			env1.setAttribute('height', '0.1');
			env1.setAttribute('depth', '0.01');
			env1.setAttribute('width', '0.15');
			env1.setAttribute('material', 'color:white; opacity:0.25');
			env1.setAttribute('env1', {});
			document.getElementById('menuenv').appendChild(env1)
			let env1Img = document.createElement('a-plane');
			env1Img.setAttribute('position',{x:0,y:0,z:0});
			env1Img.setAttribute('height', '0.1');
			env1Img.setAttribute('id', 'env1Img');
			env1Img.setAttribute('width', '0.15');
			env1Img.setAttribute('src', '#forestimg');
			document.getElementById('env1').appendChild(env1Img);
			hasEnv1 = true;


			let env2 = document.createElement('a-box');
			env2.setAttribute('position',{x:0,y:0.22,z:0});
			env2.setAttribute('rotation',{x:0,y:-25,z:0});
			env2.setAttribute('id','env2');
			env2.setAttribute('class','remote');
			env2.setAttribute('height', '0.1');
			env2.setAttribute('depth', '0.01');
			env2.setAttribute('width', '0.15');
			env2.setAttribute('material', 'color:white; opacity:0.25');
			env2.setAttribute('env2', {});
			document.getElementById('menuenv').appendChild(env2)
			let env2Img = document.createElement('a-plane');
			env2Img.setAttribute('position',{x:0,y:0,z:0});
			env2Img.setAttribute('height', '0.1');
			env2Img.setAttribute('id', 'env2Img');
			env2Img.setAttribute('width', '0.15');
			env2Img.setAttribute('src', '#dreamimg');
			document.getElementById('env2').appendChild(env2Img);
			hasEnv2 = true;

			let env3 = document.createElement('a-box');
			env3.setAttribute('position',{x:0,y:0.34,z:0});
			env3.setAttribute('rotation',{x:0,y:-25,z:0});
			env3.setAttribute('id','env3');
			env3.setAttribute('class','remote');
			env3.setAttribute('height', '0.1');
			env3.setAttribute('depth', '0.01');
			env3.setAttribute('width', '0.15');
			env3.setAttribute('material', 'color:white; opacity:0.25');
			env3.setAttribute('env3', {});
			document.getElementById('menuenv').appendChild(env3)
			let env3Img = document.createElement('a-plane');
			env3Img.setAttribute('position',{x:0,y:0,z:0});
			env3Img.setAttribute('height', '0.1');
			env3Img.setAttribute('id', 'env3Img');
			env3Img.setAttribute('width', '0.15');
			env3Img.setAttribute('src', '#japanimg');
			document.getElementById('env3').appendChild(env3Img);
			hasEnv3 = true;

			let env4 = document.createElement('a-box');
			env4.setAttribute('position',{x:0,y:0.46,z:0});
			env4.setAttribute('rotation',{x:0,y:-25,z:0});
			env4.setAttribute('id','env4');
			env4.setAttribute('class','remote');
			env4.setAttribute('height', '0.1');
			env4.setAttribute('depth', '0.01');
			env4.setAttribute('width', '0.15');
			env4.setAttribute('material', 'color:white; opacity:0.25');
			env4.setAttribute('env4', {});
			document.getElementById('menuenv').appendChild(env4)
			let env4Img = document.createElement('a-plane');
			env4Img.setAttribute('position',{x:0,y:0,z:0});
			env4Img.setAttribute('height', '0.1');
			env4Img.setAttribute('id', 'env4Img');
			env4Img.setAttribute('width', '0.15');
			env4Img.setAttribute('src', '#Yavapaiimg');
			document.getElementById('env4').appendChild(env4Img);
			hasEnv4 = true;

			let env5 = document.createElement('a-box');
			env5.setAttribute('position',{x:0,y:0.58,z:0});
			env5.setAttribute('rotation',{x:0,y:-25,z:0});
			env5.setAttribute('id','env5');
			env5.setAttribute('class','remote');
			env5.setAttribute('height', '0.1');
			env5.setAttribute('depth', '0.01');
			env5.setAttribute('width', '0.15');
			env5.setAttribute('material', 'color:white; opacity:0.25');
			env5.setAttribute('env5', {});
			document.getElementById('menuenv').appendChild(env5)
			let env5Img = document.createElement('a-plane');
			env5Img.setAttribute('position',{x:0,y:0,z:0.0});
			env5Img.setAttribute('height', '0.1');
			env5Img.setAttribute('id', 'env4Img');
			env5Img.setAttribute('width', '0.15');
			env5Img.setAttribute('src', '#defaultimg');
			document.getElementById('env5').appendChild(env5Img);
			hasEnv5 = true;
			tip.setAttribute('visible', 'false')
		}else{
			document.getElementById('env1').remove();
			document.getElementById('env2').remove();
			document.getElementById('env3').remove();
			document.getElementById('env4').remove();
			document.getElementById('env5').remove();
			//tip.setAttribute('visible', 'true')
			show = false
		}

		});

		el.addEventListener('raycaster-intersected', function () {
			el.setAttribute('material',"color:#adadad; opacity: 0.5");
		});
		el.addEventListener('raycaster-intersected-cleared', function () {
			el.setAttribute('material',"color:white; opacity: 0.25");
		});
	}
});