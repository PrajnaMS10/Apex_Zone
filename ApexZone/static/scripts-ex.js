window.onload = addStyleToSvg;

function addStyleToSvg() {
   addStyleFor("svg-front");
   addStyleFor("svg-back");
}

function addStyleFor(svgFilePrefix) {
   let svgObject = document.getElementById(svgFilePrefix);
   let svgDocument = svgObject.contentDocument;

   // Now you can manipulate the SVG elements within svgDocument
   let svgElements = svgDocument.getElementsByClassName("hover");

   for (let i=0; i<svgElements.length; i++) {
      const svgElement = svgElements[i];
      const children = svgElement.children;

      const originalColors = [];

      for (let i = 0; i < children.length; i++) {
         originalColors[i] = children[i].style.fill;
      }

      // add hover effect
      svgElement.addEventListener("mouseover", function () {
         svgElement.style.cursor = "pointer";
         printBodyPart(svgElement.id);
         for (let i = 0; i < children.length; i++) {
            const svgItem = children[i];
            svgItem.style.fill = "green";
            svgItem.style.transition = "transform 0.3s ease";
            svgItem.style.transform = "translate(4px, -4px)";
         }
      });

      svgElement.addEventListener("mouseout", function () {
         svgElement.style.cursor = "default";
         printBodyPart("");
         for (let i = 0; i < children.length; i++) {
            const svgItem = children[i];
            svgItem.style.fill = originalColors[i];
            svgItem.style.transition = "transform 0.3s ease";
            svgItem.style.transform = "translate(0px, 0px)";
         } // Revert to original color on mouseout
      });
   }
}

function printBodyPart(bodyPartId) {
   const printElement = document.getElementById("body-part-print");
   printElement.innerHTML = bodyPartId;
}