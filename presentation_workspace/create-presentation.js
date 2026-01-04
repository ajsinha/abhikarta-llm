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
  
  // Generate all slides
  const slides = [
    "slide01.html",  // Title
    "slide02.html",  // Executive Summary
    "slide03.html",  // Key Challenges
    "slide04.html",  // Platform Architecture
    "slide05.html",  // LLM Providers
    "slide06.html",  // Agent Framework
    "slide07.html",  // Workflow DAG
    "slide08.html",  // AI Org Management
    "slide09.html",  // Security & Governance
    "slide10.html",  // Use Cases
    "slide11.html",  // Technology Stack
    "slide12.html",  // Getting Started
    "slide13.html",  // Thank You
    "slide14.html",  // Appendix: Competitive Analysis
  ];
  
  for (const slideFile of slides) {
    console.log(`Processing ${slideFile}...`);
    await html2pptx(slideFile, pptx);
  }
  
  // Save the presentation
  await pptx.writeFile("Abhikarta-LLM-Overview.pptx");
  console.log("Presentation created: Abhikarta-LLM-Overview.pptx");
}

createPresentation().catch(err => {
  console.error("Error creating presentation:", err);
  process.exit(1);
});
