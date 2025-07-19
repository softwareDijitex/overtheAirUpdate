import React, { useState, useEffect } from "react";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Modal,
  Form,
  Table,
  Badge,
  Alert,
  Spinner,
} from "react-bootstrap";
import {
  Plus,
  Pencil,
  Trash,
  HddNetwork,
  FileText,
  Download,
  Eye,
} from "react-bootstrap-icons";
import axios from "axios";

const MachineManagement = ({
  customerId,
  isAdmin = false,
  onMachineSelect,
  selectedMachine,
}) => {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingMachine, setEditingMachine] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    mac_address: "",
    description: "",
  });
  const [successMessage, setSuccessMessage] = useState("");

  const fetchMachines = async () => {
    try {
      setLoading(true);
      setError(""); // Clear any previous errors
      const endpoint = isAdmin
        ? `/api/machines/admin/customer/${customerId}`
        : `/api/machines/customer/${customerId}`;

      const response = await axios.get(endpoint);
      setMachines(response.data.machines || []);
    } catch (err) {
      // Only show error for actual API failures (4xx/5xx status codes)
      if (err.response && err.response.status >= 400) {
        setError("Failed to fetch machines");
        console.error("Error fetching machines:", err);
      } else {
        // For network errors or other issues, still show error
        setError("Failed to fetch machines");
        console.error("Error fetching machines:", err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMachines();
  }, [customerId, isAdmin]);

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(""), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingMachine) {
        // Update existing machine
        const endpoint = isAdmin
          ? `/api/machines/admin/${editingMachine.id}`
          : `/api/machines/customer/${customerId}/${editingMachine.id}`;

        await axios.put(endpoint, formData);
        setSuccessMessage("Machine updated successfully");
      } else {
        // Create new machine
        const endpoint = isAdmin
          ? `/api/machines/admin/`
          : `/api/machines/customer/${customerId}`;

        const requestData = isAdmin
          ? { ...formData, customer_id: customerId }
          : formData;

        await axios.post(endpoint, requestData);
        setSuccessMessage("Machine created successfully");
      }

      setShowModal(false);
      setEditingMachine(null);
      setFormData({ name: "", mac_address: "", description: "" });
      fetchMachines();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to save machine");
      console.error("Error saving machine:", err);
    }
  };

  const handleEdit = (machine) => {
    setEditingMachine(machine);
    setFormData({
      name: machine.name,
      mac_address: machine.mac_address,
      description: machine.description,
    });
    setShowModal(true);
  };

  const handleDelete = async (machineId) => {
    if (!window.confirm("Are you sure you want to delete this machine?")) {
      return;
    }

    try {
      const endpoint = isAdmin
        ? `/api/machines/admin/${machineId}`
        : `/api/machines/customer/${customerId}/${machineId}`;

      await axios.delete(endpoint);
      setSuccessMessage("Machine deleted successfully");

      // If the deleted machine was selected, clear the selection
      if (selectedMachine && selectedMachine.id === machineId) {
        onMachineSelect(null);
      }

      fetchMachines();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to delete machine");
      console.error("Error deleting machine:", err);
    }
  };

  const handleCreate = () => {
    setEditingMachine(null);
    setFormData({ name: "", mac_address: "", description: "" });
    setShowModal(true);
  };

  const handleMachineClick = (machine) => {
    if (onMachineSelect) {
      onMachineSelect(machine);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
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
      <Row className="mb-3">
        <Col>
          <h2>
            <HddNetwork className="me-2" />
            Machine Management
          </h2>
        </Col>
        <Col xs="auto">
          <Button variant="primary" onClick={handleCreate}>
            <Plus className="me-1" />
            Add Machine
          </Button>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert
          variant="success"
          dismissible
          onClose={() => setSuccessMessage("")}
        >
          {successMessage}
        </Alert>
      )}

      {machines.length === 0 ? (
        <Card>
          <Card.Body className="text-center">
            <HddNetwork size={48} className="text-muted mb-3" />
            <h5>No machines found</h5>
            <p className="text-muted">
              {isAdmin
                ? "This customer has no machines yet."
                : "You have no machines yet. Add your first machine to get started."}
            </p>
            <Button variant="primary" onClick={handleCreate}>
              <Plus className="me-1" />
              Add Machine
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {machines.map((machine) => (
            <Col key={machine.id} lg={6} xl={4} className="mb-3">
              <Card
                className={`machine-card ${
                  selectedMachine && selectedMachine.id === machine.id
                    ? "border-primary"
                    : ""
                }`}
                style={{ cursor: "pointer" }}
                onClick={() => handleMachineClick(machine)}
              >
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <div>
                    <HddNetwork className="me-2" />
                    <strong>{machine.name}</strong>
                  </div>
                  <Badge bg="secondary">{machine.mac_address}</Badge>
                </Card.Header>
                <Card.Body>
                  {machine.description && (
                    <p className="text-muted mb-2">{machine.description}</p>
                  )}
                  <small className="text-muted">
                    Created: {formatDate(machine.created_at)}
                  </small>
                </Card.Body>
                <Card.Footer>
                  <div className="d-flex justify-content-between">
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(machine);
                      }}
                    >
                      <Pencil className="me-1" />
                      Edit
                    </Button>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(machine.id);
                      }}
                    >
                      <Trash className="me-1" />
                      Delete
                    </Button>
                  </div>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* Create/Edit Machine Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingMachine ? "Edit Machine" : "Add New Machine"}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Machine Name *</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
                placeholder="Enter machine name"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>MAC Address *</Form.Label>
              <Form.Control
                type="text"
                value={formData.mac_address}
                onChange={(e) =>
                  setFormData({ ...formData, mac_address: e.target.value })
                }
                required
                placeholder="e.g. 00:1A:2B:3C:4D:5E"
              />
              <Form.Text className="text-muted">
                Must be unique across all customers. Format: XX:XX:XX:XX:XX:XX
              </Form.Text>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Enter machine description"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {editingMachine ? "Update" : "Create"} Machine
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default MachineManagement;
