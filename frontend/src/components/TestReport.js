import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Typography,
} from "@mui/material";

export default function TestReport() {
  const [mac, setMac] = useState("");
  const [loading, setLoading] = useState(false);

  const getReport = async () => {
    setLoading(true);

    try {
      const response = await axios.post(
        "/api/test/report",

        {
          mac_address: mac,
        },

        {
          responseType: "blob",
        },
      );

      const url = window.URL.createObjectURL(response.data);

      const a = document.createElement("a");

      a.href = url;
      a.download = "Report.pdf";

      a.click();
    } catch (e) {
      alert("Report generation failed.");
    }

    setLoading(false);
  };

  return (
    <Container maxWidth="sm">
      <Paper sx={{ p: 4, mt: 5 }}>
        <Typography variant="h5">MQTT Report Test</Typography>

        <TextField
          fullWidth
          sx={{ mt: 3 }}
          label="MAC Address"
          value={mac}
          onChange={(e) => setMac(e.target.value)}
        />

        <Button
          sx={{ mt: 3 }}
          fullWidth
          variant="contained"
          onClick={getReport}
          disabled={loading}
        >
          {loading ? <CircularProgress size={22} /> : "Get Report"}
        </Button>
      </Paper>
    </Container>
  );
}
