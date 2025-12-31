const pptxgen = require("pptxgenjs");
const { html2pptx } = require("./html2pptx");

async function createPresentation() {
  const pptx = new pptxgen();
  
  // Presentation metadata
  pptx.title = "Abhikarta-LLM";
  pptx.subject = "Enterprise AI Orchestration Platform";
  pptx.author = "Ashutosh Sinha";
  pptx.company = "Abhikarta";
  pptx.layout = "LAYOUT_16x9";
  
  // Generate all 51 slides
  const slides = [];
  for (let i = 1; i <= 51; i++) {
    slides.push(`slide${i.toString().padStart(2, '0')}.html`);
  }
  
  for (const slideFile of slides) {
    console.log(`Processing ${slideFile}...`);
    await html2pptx(slideFile, pptx);
  }
  
  // Save the presentation
  await pptx.writeFile({ fileName: "Abhikarta-LLM-Overview.pptx" });
  console.log("Presentation created: Abhikarta-LLM-Overview.pptx");
}

createPresentation().catch(err => {
  console.error("Error creating presentation:", err);
  process.exit(1);
});
