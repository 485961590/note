1浏览器解析顺序是这样的，URL 解析器，HTML 解析器， CSS 解析器，JS解析器URL的解码是在后台服务检测之前的，可以理解为后台收到URL后会自动进行解码，然后才是执行开发人员编写的对URL中的值的检测函数，首先URL编码作用不在于绕过后台检测，但是当我们是GET方式提交数据时，而我们提交的数据中进行了实体编码，也就意味着存在&，#这样的特殊字符，这时就需要对这些特殊字符进行URL编码，这样才会保证正常解析，如果不进行URL编码的话，就会把+认为是空格了，而&也会是被认为用来连接URL中参数的连接符，故需要进行URL编码。如果是以POST方式传递值，就不需要进行URL编码了。CSS解析器是用来解析CSS代码的，我们暂时先不做研究。
我们重点看的是:
	htm]实体编码(HTML解析器)&#十进制;或者&#x十六进制:
	Js编码(JS解析器)\u00十六进制，也就是unicode编码
```html
<head>

</head>
<body>
	<input id="xssr_in" type="text" name="message"/><input id="postsubmit" 
	type="submit"name='submit" value="submit"/></body>
	<script>
		var btn =document.getElementById('postsubmit');
		btn.onclick = function(){
			var val=document.getElementById('xssr in').value;
			document.write(val);
	</script>
</htm1>
```

实体编码要在不破坏DOM树的构成，对于有语法结构的标签名、属性名、标签名就不能进行实体编码，对属性的值，标签之间的文本节点能够进行实体编码，**而]s编码只能对位于]S解析环境内字符进行编码且不能是括号、双引号、单引号等构成特殊意义的特殊字符**，比如alert(1)中的括号就不能进行实体编码，而且在]s编码环境中不会进行实体编码解析，但有个例外，在javascript伪协议中，比如test，即可以把javascript:alert('test’):这一部分看成是标签a的属性href的值，从而能够进行<>编码会被正常实体编码解析，又可以对alert或alert中的字符进行]s编码，但对alert中的字符编码没什么实际作用.
	如果是输出到了js代码中，再由js代码输出到htm1中，那么js会先将unicode编码进行解析，然后再输出到htm1中，这就有了htm标签效果。如下:
```javascript
<script>
	var btn= document.getElementById('postsubmit');btn.onclick =function({
	var val =document.getElementById('xssr in').value;
	document.write(" u003c u0073\u0063 u0072\u0069\y0070\u0074\u003e u0061\u006c u0065\u0072u0074\u0028\u0031\u0032\y0033\u0029\u003b\u003c\u002f\u0073\u0063\u0072\u0069\u0070\u0074u003e");
</script>
```
