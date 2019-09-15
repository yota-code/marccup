

function process_svg_math() {
	var svg_ns = "http://www.w3.org/2000/svg";

	var h_math_collection = document.getElementsByClassName("s_math");
	while ( h_math_collection.length ) {
		var h_math = h_math_collection[0];

		var h_math_container = h_math.firstChild;
		var h_math_svg = h_math_container.firstChild;
		if ( h_math_container.tagName.toLowerCase() === "mjx-container" && h_math_svg.tagName.toLowerCase() === "svg") {
			h_math_svg.removeAttribute("xmlns");
			h_math_svg.removeAttribute("xmlns:xlink");

			var pos_x = h_math.getAttribute("x");
			var pos_y = h_math.getAttribute("y");

			var h_g = document.createElementNS(svg_ns, 'g');
			h_g.grow('g', {transform:"translate("+20+" "+20+")"}, "svg").appendChild(h_math_svg);

			h_math.parentNode.replaceChild(h_g, h_math);

			var bbox = h_math_svg.getBoundingClientRect();

			if ( h_math.tagName.toLowerCase() === "rect" ) {
				var m_x = pos_x - bbox.width / 2;
				var m_y = pos_y - bbox.height / 2;
				h_g.grow('rect', {
					class: "diag_rect",
					x:pos_x - (bbox.width + 40) / 2,
					y:pos_y - (bbox.height + 30) / 2,
					width:bbox.width + 40,
					height:bbox.height + 30
				}, "svg", true);
			} else {
				var m_x = pos_x - bbox.width / 2;
				var m_y = pos_y - bbox.height - 2;
			}
			h_math_svg.parentNode.setAttribute("transform", "translate("+ m_x +" "+ m_y +")");


		}
		else {
			console.log("ERROR");
		}
	}

}

