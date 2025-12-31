const pptxgen = require("pptxgenjs");
const { html2pptx } = require("./html2pptx");

async function test() {
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_16x9";
  
  for (let i = 1; i <= 5; i++) {
    const file = `slide${i.toString().padStart(2, '0')}.html`;
    console.log(`Testing ${file}...`);
    try {
      await html2pptx(file, pptx);
      console.log(`  ✓ ${file} OK`);
    } catch (err) {
      console.log(`  ✗ ${file} FAILED: ${err.message}`);
    }
  }
  
  await pptx.writeFile({ fileName: "test.pptx" });
  console.log("Test presentation saved");
}

test().catch(console.error);
