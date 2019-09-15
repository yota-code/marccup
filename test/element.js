
Element.prototype.add_text = function (txt) {
	this.appendChild(
		document.createTextNode(txt)
	)
	return this;
};

Element.prototype.clear = function () {
	while (this.firstChild) {
		this.removeChild(this.firstChild);
	}
	return this;
};

Element.prototype.grow = function (tag, attribute_map, name_space, prepend) {
	if ( prepend === undefined ) {
		prepend = false;
	} else {
		prepend = Boolean(prepend);
	}

	if ( name_space !== undefined ) {
		
		switch ( name_space ) {
			case "html" :
				name_space = "http://www.w3.org/1999/xhtml";
				break;
			case "svg" :
				name_space = "http://www.w3.org/2000/svg";
				break;
			case "xbl" :
				name_space = "http://www.mozilla.org/xbl";
				break;
			case "xul" :
				name_space = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul";
				break;
		}		
		
		var child = document.createElementNS(name_space, tag);
	} else {
		var child = document.createElement(tag);
	}
	
	if ( attribute_map !== undefined ) {
		for (let key in attribute_map) {
			child.setAttribute(key, attribute_map[key]);
		}
	}
	
	if ( prepend ) {
		this.prepend(child);
	} else {
		this.append(child);
	}
	
	return child;
};
