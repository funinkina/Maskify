const express = require("express");
const multer = require("multer");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const app = express();
const port = 3000;

// Middleware to parse URL-encoded bodies (e.g., form data)
app.use(express.urlencoded({ extended: true }));

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  },
});

const upload = multer({ storage: storage });

// Create the uploads directory if it doesn't exist
if (!fs.existsSync("uploads")) {
  fs.mkdirSync("uploads");
}

// Endpoint to upload a file and process it
app.post("/process-file", upload.single("file"), (req, res) => {
  //get redaction level from the request and the file path
  const inputFilePath = req.file.path;
  const redactionLevel = req.body.level;
  // Call the Python script with the input file path and redaction level
  const python = spawn("python", [
    path.join(__dirname, "redaction.py"),
    inputFilePath,
    redactionLevel,
  ]);

  python.on("close", (code) => {
    console.log(`Python script exited with code ${code}`);
    const outputFilePath = inputFilePath.replace(
      path.extname(req.file.originalname),
      "_masked.jpg"
    );

    if (code !== 0) {
      return res.status(500).send("Error processing file");
    }

    // Ensure the output file exists before sending it
    fs.access(outputFilePath, fs.constants.F_OK, (err) => {
      if (err) {
        return res
          .status(500)
          .send("Redaction Failed Output File not generated");
      }

      // Send the processed file back to the client
      res.sendFile(path.resolve(outputFilePath), (err) => {
        if (err) {
          console.error("Error sending file:", err);
        }
        // Clean up files
        fs.unlink(inputFilePath, (err) => {
          if (err) console.error("Error deleting input file:", err);
        });
        fs.unlink(outputFilePath, (err) => {
          if (err) console.error("Error deleting output file:", err);
        });
      });
    });
  });

  python.on("error", (err) => {
    res.status(500).send("Failed to start Python script");
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
