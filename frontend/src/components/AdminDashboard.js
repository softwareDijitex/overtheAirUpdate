import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import axios from "axios";
import {
  Card,
  Button,
  Form,
  Table,
  Alert,
  Modal,
  Badge,
  Row,
  Col,
  Container,
  Nav,
  Tab,
  Spinner,
} from "react-bootstrap";
import {
  HddNetwork,
  FileText,
  Upload,
  Download,
  Eye,
  Trash,
  Plus,
  Person,
} from "react-bootstrap-icons";
import MachineManagement from "./MachineManagement";

const AdminDashboard = () => {
  const { user, token } = useAuth();
  const [customers, setCustomers] = useState([]);
  const [activeTab, setActiveTab] = useState("customers");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [machines, setMachines] = useState([]);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [versionNumber, setVersionNumber] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showVersionsModal, setShowVersionsModal] = useState(false);
  const [selectedFileVersions, setSelectedFileVersions] = useState([]);
  const [selectedFileName, setSelectedFileName] = useState("");

  // File upload state for admin
  const [selectedCustomerForUpload, setSelectedCustomerForUpload] =
    useState("");
  const [selectedMachineForUpload, setSelectedMachineForUpload] = useState("");

  useEffect(() => {
    if (token) {
      fetchCustomers();
    }
  }, [token]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);



  // useEffect(() => {
  //   console.log("Hello");
  // }, [selectedFileVersions]);


  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await axios.get("http://localhost:8000/api/customers/", {
        headers: {
          Authorization: `Bearer ${token}`, // Make sure you have the admin token here
        },
      });
      setCustomers(response.data);
    } catch (error) {
      setError("Failed to fetch customers");
      console.error("Error fetching customers:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomerMachines = async (customerId) => {
    try {
      const response = await axios.get(
        `/api/machines/admin/customer/${customerId}`
      );
      setMachines(response.data || []);
    } catch (error) {
      setError("Failed to fetch customer machines");
      console.error("Error fetching machines:", error);
    }
  };

  const fetchMachineFiles = async (customerId, machineId) => {
    try {
      // Use admin-specific endpoint for file listing
      const response = await axios.get(
        `/api/files/admin/machine/${customerId}/${machineId}`
      );
      setFiles(response.data.files || []);
    } catch (error) {
      setError("Failed to fetch files");
      console.error("Error fetching files:", error);
    }
  };

  const handleCustomerSelect = async (customer) => {
    setSelectedCustomer(customer);
    await fetchCustomerMachines(customer.customer_id);
    setSelectedMachine(null);
    setFiles([]);
    // Automatically switch to machines tab
    setActiveTab("machines");
  };

  const handleMachineSelect = (machine) => {
    setSelectedMachine(machine);
    fetchMachineFiles(selectedCustomer.customer_id, machine.id);
    // Automatically switch to files tab
    setActiveTab("files");
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 7 * 1024 * 1024) {
        // 2MB limit
        setError("File size must be less than 2MB");
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setError("");

      // Auto-suggest next version number if file with same name exists
      const existingFile = files.find((f) => f.filename === file.name);
      if (existingFile) {
        // Try to increment the latest version
        const latestVersion = existingFile.version;
        try {
          // If it's a number, increment it
          const numVersion = parseFloat(latestVersion);
          if (!isNaN(numVersion)) {
            setVersionNumber((numVersion + 1).toString());
          } else {
            // If it's a string, append a number
            setVersionNumber(latestVersion + "_1");
          }
        } catch {
          setVersionNumber(latestVersion + "_1");
        }
      } else {
        setVersionNumber("1");
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setError("Please select a file");
      return;
    }

    if (!selectedMachine) {
      setError("Please select a machine");
      return;
    }

    if (!versionNumber || versionNumber.trim() === "") {
      setError("Please enter a version number");
      return;
    }

    const version = versionNumber.trim();
    await performUpload(selectedFile, version);
  };

  const performUpload = async (file, version) => {
    setUploading(true);
    setError("");
    setSuccess("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("version", version);
    formData.append("customer_id", selectedCustomer.customer_id);
    formData.append("machine_id", selectedMachine.id);

    try {
      await axios.post(`/api/files/admin/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSuccess("File uploaded successfully!");
      setSelectedFile(null);
      setVersionNumber("");
      // Reset the file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.value = "";
      }
      fetchMachineFiles(selectedCustomer.customer_id, selectedMachine.id);
    } catch (error) {
      const errorMessage = error.response?.data?.error || "Upload failed";
      setError(errorMessage);

      // If the error is about version already existing, suggest a new version
      if (
        errorMessage.includes("already exists") &&
        errorMessage.includes("version")
      ) {
        // Try to suggest next version
        try {
          const numVersion = parseFloat(version);
          if (!isNaN(numVersion)) {
            setVersionNumber((numVersion + 1).toString());
          } else {
            setVersionNumber(version + "_1");
          }
        } catch {
          setVersionNumber(version + "_1");
        }
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (filename, version) => {
    try {
      const response = await axios.get(
        `/api/files/admin/download/${selectedCustomer.customer_id}/${selectedMachine.id}/${filename}/${version}`,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      setError("Download failed");
    }
  };

  const handleViewVersions = async (filename) => {
    try {
      const response = await axios.get(
        `/api/files/admin/versions/${selectedCustomer.customer_id}/${selectedMachine.id}/${filename}`
      );
      setSelectedFileVersions(response.data.versions || []);
      setSelectedFileName(filename);
      setShowVersionsModal(true);
    } catch (error) {
      setError("Failed to fetch versions");
    }
  };

  const handleDeleteFile = async (filename, version) => {
    if (
      !window.confirm(
        `Are you sure you want to delete ${filename} version ${version}?`
      )
    ) {
      return;
    }

    try {
      await axios.delete(
        `/api/files/admin/delete/${selectedCustomer.customer_id}/${selectedMachine.id}/${filename}/${version}`
      );
      
      setSelectedFileVersions(prevVersions => 
        
        prevVersions.filter(v => v.version !== version)
      );
      setSuccess("File deleted successfully");
      console.log("Hello");
      fetchMachineFiles(selectedCustomer.customer_id, selectedMachine.id);
    } catch (error) {
      setError("Failed to delete file");
    }
  };

  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <Container className="text-center mt-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  return (
    <Container>
      <h2 className="mb-4">Admin Dashboard</h2>

      {error && (
        <Alert variant="danger" onClose={() => setError("")} dismissible>
          {error}
        </Alert>
      )}
      {success && (
        <Alert variant="success" onClose={() => setSuccess("")} dismissible>
          {success}
        </Alert>
      )}

      <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
        <Row>
          <Col>
            <Nav variant="tabs" className="mb-3">
              <Nav.Item>
                <Nav.Link eventKey="customers">
                  <Person className="me-2" />
                  Customers ({customers.length})
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="machines" disabled={!selectedCustomer}>
                  <HddNetwork className="me-2" />
                  Machines
                  {selectedCustomer && (
                    <Badge bg="secondary" className="ms-2">
                      {selectedCustomer.name}
                    </Badge>
                  )}
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="files" disabled={!selectedMachine}>
                  <FileText className="me-2" />
                  Files
                  {selectedMachine && (
                    <Badge bg="secondary" className="ms-2">
                      {selectedMachine.name}
                    </Badge>
                  )}
                </Nav.Link>
              </Nav.Item>
            </Nav>

            <Tab.Content>
              <Tab.Pane eventKey="customers">
                <Card>
                  <Card.Header>
                    <h5>Customer Management</h5>
                  </Card.Header>
                  <Card.Body>
                    {customers.length === 0 ? (
                      <p className="text-muted">No customers registered yet.</p>
                    ) : (
                      <Table responsive>
                        <thead>
                          <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Address</th>
                            <th>Registered</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {customers.map((customer, index) => (
                            <tr key={index}>
                              <td>{customer.name}</td>
                              <td>{customer.email}</td>
                              <td>{customer.phone}</td>
                              <td>{customer.address}</td>
                              <td>{formatDate(customer.created_at)}</td>
                              <td>
                                <Button
                                  variant="outline-primary"
                                  size="sm"
                                  onClick={() => handleCustomerSelect(customer)}
                                  title="View Customer Machines"
                                >
                                  <HddNetwork className="me-1" />
                                  View Machines
                                </Button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    )}
                  </Card.Body>
                </Card>
              </Tab.Pane>

              <Tab.Pane eventKey="machines">
                {!selectedCustomer ? (
                  <Card>
                    <Card.Body className="text-center">
                      <HddNetwork size={48} className="text-muted mb-3" />
                      <h5>No Customer Selected</h5>
                      <p className="text-muted">
                        Please select a customer from the Customers tab to view
                        their machines.
                      </p>
                    </Card.Body>
                  </Card>
                ) : (
                  <MachineManagement
                    customerId={selectedCustomer.customer_id}
                    isAdmin={true}
                    onMachineSelect={handleMachineSelect}
                    selectedMachine={selectedMachine}
                  />
                )}
              </Tab.Pane>

              <Tab.Pane eventKey="files">
                {!selectedMachine ? (
                  <Card>
                    <Card.Body className="text-center">
                      <FileText size={48} className="text-muted mb-3" />
                      <h5>No Machine Selected</h5>
                      <p className="text-muted">
                        Please select a machine from the Machines tab to manage
                        its files.
                      </p>
                    </Card.Body>
                  </Card>
                ) : (
                  <>
                    {/* File Upload Section */}
                    <Card className="mb-4">
                      <Card.Header>
                        <h5>
                          <Upload className="me-2" />
                          Upload New File to {selectedMachine.name}
                        </h5>
                      </Card.Header>
                      <Card.Body>
                        <Form onSubmit={handleUpload}>
                          <Row>
                            <Col md={6}>
                              <Form.Group className="mb-3">
                                <Form.Label>Select File (Max 2MB) *</Form.Label>
                                <Form.Control
                                  type="file"
                                  onChange={handleFileSelect}
                                  accept="*/*"
                                  required
                                />
                              </Form.Group>
                            </Col>
                            <Col md={6}>
                              <Form.Group className="mb-3">
                                <Form.Label>Version Number *</Form.Label>
                                <Form.Control
                                  type="text"
                                  placeholder="Enter version (e.g., 1, 1.1, beta, etc.)"
                                  value={versionNumber}
                                  onChange={(e) =>
                                    setVersionNumber(e.target.value)
                                  }
                                  required
                                />
                                <Form.Text className="text-muted">
                                  Enter any version identifier (numbers,
                                  decimals, or text)
                                </Form.Text>
                              </Form.Group>
                            </Col>
                          </Row>
                          <Button
                            variant="primary"
                            type="submit"
                            disabled={
                              uploading ||
                              !selectedFile ||
                              !versionNumber.trim()
                            }
                          >
                            {uploading ? "Uploading..." : "Upload File"}
                          </Button>
                        </Form>
                      </Card.Body>
                    </Card>

                    {/* Files List */}
                    <Card>
                      <Card.Header>
                        <h5>
                          <FileText className="me-2" />
                          Files for {selectedMachine.name}
                        </h5>
                      </Card.Header>
                      <Card.Body>
                        {files.length === 0 ? (
                          <p className="text-muted">
                            No files uploaded to this machine yet.
                          </p>
                        ) : (
                          <Table responsive>
                            <thead>
                              <tr>
                                <th>Filename</th>
                                <th>Latest Version</th>
                                <th>Total Versions</th>
                                <th>File Size</th>
                                <th>Uploaded</th>
                                <th>Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              {files.map((file, index) => (
                                <tr key={index}>
                                  <td>{file.filename}</td>
                                  <td>
                                    <Badge bg="primary">v{file.version}</Badge>
                                  </td>
                                  <td>
                                    <Badge bg="info">
                                      {file.total_versions}
                                    </Badge>
                                  </td>
                                  <td>{formatFileSize(file.file_size)}</td>
                                  <td>{formatDate(file.uploaded_at)}</td>
                                  <td>
                                    <Button
                                      variant="outline-primary"
                                      size="sm"
                                      className="me-1"
                                      onClick={() =>
                                        handleDownload(
                                          file.filename,
                                          file.version
                                        )
                                      }
                                    >
                                      <Download className="me-1" />
                                      Download
                                    </Button>
                                    <Button
                                      variant="outline-secondary"
                                      size="sm"
                                      className="me-1"
                                      onClick={() =>
                                        handleViewVersions(file.filename)
                                      }
                                    >
                                      <Eye className="me-1" />
                                      Versions
                                    </Button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        )}
                      </Card.Body>
                    </Card>
                  </>
                )}
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Tab.Container>

      {/* Versions Modal */}
      <Modal
        show={showVersionsModal}
        onHide={() => setShowVersionsModal(false)}
        size="lg"
      >
        <Modal.Header closeButton>
          <Modal.Title>File Versions - {selectedFileName}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Table responsive>
            <thead>
              <tr>
                <th>Version</th>
                <th>File Size</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {selectedFileVersions.map((version, index) => (
                <tr key={index}>
                  <td>
                    <Badge bg="primary">v{version.version}</Badge>
                  </td>
                  <td>{formatFileSize(version.file_size)}</td>
                  <td>{formatDate(version.uploaded_at)}</td>
                  <td>
                    <Button
                      variant="outline-primary"
                      size="sm"
                      className="me-1"
                      onClick={() =>
                        handleDownload(selectedFileName, version.version)
                      }
                    >
                      <Download className="me-1" />
                      Download
                    </Button>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() =>
                        handleDeleteFile(selectedFileName, version.version)
                      }
                    >
                      <Trash className="me-1" />
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default AdminDashboard;
