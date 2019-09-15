

function process_block_diagram() {
	var svg_ns = "http://www.w3.org/2000/svg";

	var h_text_collection = document.getElementsByClassName("s_math");
	while ( h_text_collection.length ) {
		var h_text = h_text_collection[0];

		console.log("---------------- ");
		console.log(h_text);

		var h_math_container = h_text.firstChild;
		var h_math_svg = h_math_container.firstChild;
		if ( h_math_container.tagName.toLowerCase() === "mjx-container" && h_math_svg.tagName.toLowerCase() === "svg") {
			h_math_svg.removeAttribute("xmlns");
			h_math_svg.removeAttribute("xmlns:xlink");

			var pos_x = h_text.getAttribute("x");
			var pos_y = h_text.getAttribute("y");

			var h_g = document.createElementNS(svg_ns, 'g');
			h_g.grow('g', {transform:"translate("+20+" "+20+")"}, "svg").appendChild(h_math_svg);
			
			h_text.parentNode.replaceChild(h_g, h_text);

			var bbox = h_math_svg.getBoundingClientRect();
			h_math_svg.parentNode.setAttribute("transform", "translate("+ ( pos_x - bbox.width / 2 ) +" "+ ( pos_y - bbox.height / 2 ) +")");

			h_g.grow('rect', {
				class: "block_rect",
				x:pos_x - (bbox.width + 40) / 2,
				y:pos_y - (bbox.height + 30) / 2,
				width:bbox.width + 40,
				height:bbox.height + 30
			}, "svg");


		}
		else {
			console.log("ERROR");
		}
	}

}

