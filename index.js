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
  const inputFilePath = req.file.path;
  console.log("inputFilePath", inputFilePath);
  const redactionLevel = req.body.level;

  const python = spawn("python", [
    path.join(__dirname, "redaction.py"),
    inputFilePath,
    redactionLevel,
  ]);

  // Capture stdout (standard output)
  python.stdout.on("data", (data) => {
    console.log(`stdout: ${data}`);
  });

  // Capture stderr (standard error)
  python.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  python.on("close", (code) => {
    let outputFilePath = inputFilePath.replace(
      path.extname(req.file.originalname),
      "_masked.jpg"
    );
    console.log("outputFilePath", outputFilePath);
    outputFilePath = outputFilePath.replace("uploads/", "");
    console.log("outputFilePath", outputFilePath);

    if (code !== 0) {
      // Ensure only one response is sent
      if (!res.headersSent) {
        return res.status(500).send("Error processing file");
      }
      return;
    }

    // Ensure the output file exists before sending it
    fs.access(outputFilePath, fs.constants.F_OK, (err) => {
      if (err) {
        // Ensure only one response is sent
        if (!res.headersSent) {
          return res
            .status(500)
            .send("Redaction Failed Output File not generated");
        }
        return;
      }

      // Send the processed file back to the client
      res.sendFile(path.resolve(outputFilePath), (err) => {
        if (err) {
          console.error("Error sending file:", err);
        }
        // Clean up files after sending response
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
    // Ensure only one response is sent
    if (!res.headersSent) {
      res.status(500).send("Failed to start Python script");
    }
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
