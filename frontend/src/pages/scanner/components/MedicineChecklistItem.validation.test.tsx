import { render, screen, fireEvent } from "@testing-library/react";
import MedicineChecklistItem from "./MedicineChecklistItem";
import { Modal } from "@chakra-ui/react";

jest.mock("@chakra-ui/react", () => ({
  Modal: {
    isOpen: jest.fn(),
    onClose: jest.fn(),
    ModalOverlay: () => null,
    ModalContent: () => null,
    ModalHeader: () => null,
    ModalBody: () => null,
    ModalCloseButton: () => null,
  },
  Button: {
    variant: jest.fn(),
    size: jest.fn(),
    colorScheme: jest.fn(),
    isLoading: jest.fn(),
  },
}));

const mockMedicine = {
  medicineId: 123,
  name: "Unknown Medicine",
  genericName: null,
  brandName: null,
  type: "tablet",
};

const baseProps = {
  id: "row-unknown",
  medicine: mockMedicine,
  onToggle: jest.fn(),
  onSelectAll: jest.fn(),
  onClearAll: jest.fn(),
  onEdit: jest.fn(),
  onLookup: jest.fn(),
  onSubmit: jest.fn(),
  onResolveDuplicate: jest.fn(),
  onSubmitAll: jest.fn(),
  isSubmitting: false,
  isKnown: false,
  isDuplicate: false,
  editField: undefined,
  editValue: "",
};

describe("MedicineChecklistItem - validation & unknown flow", () => {
  it("prevents submission with empty quantity", async () => {
    const onSubmit = jest.fn();
    render(<MedicineChecklistItem {...baseProps, onSubmit} quantity={""} unit={""} expiryDate={"2025-01-01"} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    // Wait for validation error to appear
    expect(screen.getByText(/quantity is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("prevents submission with invalid quantity", async () => {
    const onSubmit = jest.fn();
    render(<MedicineChecklistItem {...baseProps, onSubmit} quantity={"0"} unit={"tablet"} expiryDate={"2025-01-01"} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    expect(screen.getByText(/quantity must be > 0/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("prevents submission with empty unit", async () => {
    const onSubmit = jest.fn();
    render(<MedicineChecklistItem {...baseProps, onSubmit} quantity={"5"} unit={""} expiryDate={"2025-01-01"} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    expect(screen.getByText(/unit is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("prevents submission with invalid expiry format", async () => {
    const onSubmit = jest.fn();
    render(<MedicineChecklistItem {...baseProps, onSubmit} quantity={"5"} unit={"tablet"} expiryDate={"invalid"} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    expect(screen.getByText(/invalid date format/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("shows unknown medicine confirmation dialog before submission", async () => {
    const onSubmit = jest.fn();
    render(<MedicineChecklistItem {...baseProps, onSubmit} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    // Confirmation dialog should appear
    await screen.findByText(/unknown medicine/i);
    expect(screen.getByText(/create anyway/i)).toBeInTheDocument();
  });

  it("allows submission after confirming unknown medicine", async () => {
    const mockSubmit = jest.fn();
    render(
      <MedicineChecklistItem
        {...baseProps}
        onSubmit={mockSubmit}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    // Click "Create Anyway"
    const createBtn = screen.getByRole("button", { name: /create anyway/i });
    fireEvent.click(createBtn);
    await screen.findByText(/unknown medicine/i).then(() => {
      expect(mockSubmit).toHaveBeenCalledTimes(1);
    });
  });

  it("submits successfully when all fields are valid", async () => {
    const onSubmit = jest.fn();
    render(
      <MedicineChecklistItem
        {...baseProps}
        quantity={"10"}
        unit={"box"}
        expiryDate={"2028-12-31"}
        onSubmit={onSubmit}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    await screen.findByText(/added successfully/i);
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        id: "row-unknown",
        medicineId: 123,
        medicineName: "Unknown Medicine",
        quantity: 10,
        quantityUnit: "box",
        expiryDate: "2028-12-31",
      })
    );
  });
});