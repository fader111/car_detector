/* часть функций JS, те, что получилось вытащить, выынесены сюда */	
/* Функция создаёт кроссбраузерный объект XMLHTTP для отправки данных на сервер*/
function getXmlHttp() {
	var xmlhttp;
	try {
	  xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
	} catch (e) {
	try {
	  xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	} catch (E) {
	  xmlhttp = false;
	}
	}
	if (!xmlhttp && typeof XMLHttpRequest!='undefined') {
	  xmlhttp = new XMLHttpRequest();
	}
	return xmlhttp;
};

// создает полигон и возвращает его
function create_path(dx,dy,x,y){
	//console.log("pt=",pt);
	var pt; // тут нельзя этого писать так передается масссив всех полигонов, надо его передавать как параметр
	
	var stSize =50; // размеры вновь создаваемого полигона 
	if (dx<stSize&dy<stSize) pt = ["M", x0, y0, "L",x0+stSize,y0,"L",x0+stSize,y0+stSize,"L",x0,y0+stSize,"Z"].concat(pt);
	else if (dx<stSize) pt = ["M", x0, y0, "L",x0+stSize,y0,"L",x0+stSize,y,"L",x0,y,"Z"].concat(pt);
	else if (dy<stSize) pt = ["M", x0, y0, "L",x,y0,"L",x,y0+stSize,"L",x0,y0+stSize,"Z"].concat(pt);
	else pt = ["M", x0, y0, "L",x,y0,"L",x,y,"L",x0,y,"Z"].concat(pt);
	return pt;
};

		
// функция отсылает данные полигонов на сервер
function sendPolyToServerPHP(req) {
	var xmlhttp = getXmlHttp(); // Создаём объект XMLHTTP
	xmlhttp.open('POST', '', true); // Открываем асинхронное соединение чтоб браузер не ждал
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Отправляем кодировку (не выключать)
	xmlhttp.send("req=" + encodeURIComponent(req)); // Отправляем POST-запрос
	xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера (не используем пока)
	  if (xmlhttp.readyState == 4) { // Ответ пришёл
		if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
			//console.log("Polygones saved. Server says 200!!___");//,encodeURIComponent(req));
		}
	  }
	};
}

function convertPolyToString(polygones,W,H,modes_poly,ramkiArrows){ // формирует JSON структуру из рамок 
	currState =0; //режим работы рамки 0-Проезд(П), 1-Остановка(О)
	var string='{\n"polygones":\n[\n';
	for (var i=0;i<polygones.length;i++){ // формируем координаты точек полигонов
		string += "[\n";
		for (var j=0;j<4;j++){
			string += "[";
			string+=polygones[i].attr("path")[j][1]; // координата X точки полигона
			string+=",";
			string+=polygones[i].attr("path")[j][2]; // координата Y точки полигона
			if (j<3) string += "],\n";
			else string += "]\n";
		}
		if (i<polygones.length-1) string += "],\n";
		else string += "]\n";
	}
	string += ']\n,"frame":\n['+W+","+H+"]";
	string += '\n,"ramkiModes":\n['; // тут добавляем в файл типы рамок
	//console.log("modes_poly from  convertPolyToString =",modes_poly);
	for (var i=0;i<modes_poly.length;i++){  //формируем режимы работы рамок 
			//strToCompare = modes_poly[i].attr("text");
			//currState =0;
			if (modes_poly[i].attr("text")=='-П')
				currState = 0;
			else if(modes_poly[i].attr("text")=='-О')
				currState = 1;
			else{
				console.log("Inpossible frame setting attr(text) = ",modes_poly[i].attr("text"),' state= ',currState);
				//currState = 1;
			}
			if (i<polygones.length-1)
				string+=currState+','; 
			else
				string+=currState+']';
	}
	string += '\n,"ramkiDirections":\n[';
	for (var i=0;i<ramkiArrows.length;i++){  //формируем структуру стрелок - номер полигона вместо r.set здесь обычный массив. т.к. перебираемый массив из r.set сделать не получилось... РАЗОБРАТЬСЯ ПОЧЕМУ...
		string += "\n[";
		for (var j=0;j<4;j++){ 
			if (ramkiArrows[i][j]==1)
				currState="1"
			else
				currState="0";
			if (j<3) string += currState+",";
			else string += currState+"]";
		}
		if (i<ramkiArrows.length-1) string += ",";
		else string += "\n";
	}	
	string += ']\n}\n';
	//console.log("string from conv",string);
	return string
}

function sendIpSettingsToServer(){
	var ip_address = document.getElementById("ip_address").value;
	var ip_netmask = document.getElementById("ip_netmask").value;
	var ip_address_gateway = document.getElementById("ip_address_gateway").value;
	var ip_address_hub = document.getElementById("ip_address_hub").value;
	var post_data = "ip_address=" + encodeURIComponent(ip_address) + "&ip_netmask=" + encodeURIComponent(ip_netmask) + "&ip_address_gateway=" + encodeURIComponent(ip_address_gateway) + "&ip_address_hub=" + encodeURIComponent(ip_address_hub);
	var xmlhttp = getXmlHttp(); // Создаём объект XMLHTTP
	xmlhttp.open('POST', 'ip_handler.php', true); // Открываем асинхронное соединение
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Отправляем кодировку (не выключать)
	xmlhttp.send("ip=" + encodeURIComponent(ip_address) + "&netmask=" + encodeURIComponent(ip_netmask) + "&gateway=" + encodeURIComponent(ip_address_gateway) + "&hub=" + encodeURIComponent(ip_address_hub)); // Отправляем POST-запрос
	xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера (не используем пока)
		if (xmlhttp.readyState == 4) { // Ответ пришёл
			if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
				console.log("IP settings sent!!");
				document.getElementById("IP_settings_data").innerHTML = xmlhttp.responseText; // Выводим ответ сервера
			}
		}			
	}		
}

function getStatusFromServerPHP(polygones) {
	var xmlhttp = getXmlHttp(); // Создаём объект XMLHTTP
	xmlhttp.open('POST', 'post_handler_status.php', true); // Открываем асинхронное соединение
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Отправляем кодировку (не выключать)
	xmlhttp.send("req_st=" + encodeURIComponent(0)); // Отправляем POST-запрос
	xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера (не используем пока)
		if(xmlhttp.readyState == 4) { // Ответ пришёл
			if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
				document.getElementById("polyData").innerHTML = "state: "+xmlhttp.responseText; // Выводим ответ сервера
				polyStatus = xmlhttp.responseText;
				status='';
				for(i=0;i<polyStatus.length;i++){
					if( polyStatus[i] == '0' | polyStatus[i] == '1' ) status += polyStatus[i];
				};
				for (i=0;i<(polygones.length);i++){
					if (status[i]==0)polygones[i].attr({stroke:"red",fill:"red"});
					else if (status[i]==1)polygones[i].attr({stroke:"green",fill:"green"});
				}
			}
		}
	};
}

// кандидат на удаление т.к. теперь этот функционал объединен с основным, рисующим полигоны (ff)
function createPolygonesOnLoad(req){
	polyFromServer = getPolyFromServerPHP(req);
	//console.log('polyFromServer',polyFromServer);
	path=[];
	var delayedPolygonesDraw = function(){
		//console.log('polyFromServer after createOnload',polyFromServer);
		for (i=0;i<polyFromServer.polygones.length;i++){
			corners = polyFromServer.polygones[i];
			path = ["M", corners[0][0], corners[0][1], "L",corners[1][0],corners[1][1],"L",corners[2][0],corners[2][1],"L",corners[3][0],corners[3][1],"Z"];
			polygones.push(r.path(path).attr({stroke:"red",fill:"red",opacity:0.5}));	
			k++;
		}
	}
	setTimeout(delayedPolygonesDraw,100);	
	setTimeout(assygnPolygonNumber,120);
}