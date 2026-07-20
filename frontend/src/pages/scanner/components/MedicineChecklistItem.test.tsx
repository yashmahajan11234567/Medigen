import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MedicineChecklistItem from "./MedicineChecklistItem";
import { Button } from "@chakra-ui/react";

// Mock data
const mockMedicine = {
  medicineId: 123,
  name: "Test Medicine",
  genericName: "Test Generic",
  brandName: "Test Brand",
  type: "tablet",
};

const mockProps = {
  id: "row-1",
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
  isKnown: true,
  isDuplicate: false,
  editField: undefined,
  editValue: "",
};

describe("MedicineChecklistItem", () => {
  // Test duplicate resolution actions
  it("calls onResolveDuplicate with 'update' when Update Qty button is clicked", () => {
    const handleResolveDuplicate = jest.fn();
    render(<MedicineChecklistItem {...mockProps} onResolveDuplicate={handleResolveDuplicate} />);
    // Find the button containing 'Update Qty' text
    const updateButton = screen.getByRole("button", { name: /update qty/i });
    fireEvent.click(updateButton);
    expect(handleResolveDuplicate).toHaveBeenCalledWith(
      expect.objectContaining({ id: "row-1" }),
      "update"
    );
  });

  it("calls onResolveDuplicate with 'skip' when Skip button is clicked", () => {
    const handleResolveDuplicate = jest.fn();
    render(<MedicineChecklistItem {...mockProps} onResolveDuplicate={handleResolveDuplicate} />);
    const skipButton = screen.getByRole("button", { name: /skip/i });
    fireEvent.click(skipButton);
    expect(handleResolveDuplicate).toHaveBeenCalledWith(
      expect.objectContaining({ id: "row-1" }),
      "skip"
    );
  });

  it("calls onResolveDuplicate with 'separate' when Separate Entry button is clicked", () => {
    const handleResolveDuplicate = jest.fn();
    render(<MedicineChecklistItem {...mockProps} onResolveDuplicate={handleResolveDuplicate} />);
    const separateButton = screen.getByRole("button", { name: /separate entry/i });
    fireEvent.click(separateButton);
    expect(handleResolveDuplicate).toHaveBeenCalledWith(
      expect.objectContaining({ id: "row-1" }),
      "separate"
    );
  });

  // Test validation for unknown medicine confirmation
  it("shows confirmation dialog when submitting unknown medicine without approval", () => {
    const mockItem = {
      ...mockProps,
      isKnown: false,
      onSubmit: jest.fn(),
    };
    render(<MedicineChecklistItem {...mockItem} />);
    // Assume the submit button triggers submission
    const submitButton = screen.getByRole("button", { name: /add to inventory/i });
    fireEvent.click(submitButton);
    // The dialog should appear
    expect(screen.getByText(/unknown medicine/i)).toBeInTheDocument();
  });

  it("submits normally when medicine is known and fields are valid", async () => {
    const mockItem = {
      ...mockProps,
      isKnown: true,
      quantity: "5",
      unit: "tablets",
      expiryDate: "2027-01-01",
      validateAllFields: jest.fn(() => true), // make validation pass
    };
    // Override the internal maybeSubmit by mocking onSubmit
    render(<MedicineChecklistItem {...mockItem} />);
    const submitButton = screen.getByRole("button", { name: /add to inventory/i });
    fireEvent.click(submitButton);
    await waitFor(() => {
      expect(mockItem.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          id: "row-1",
          medicineId: 123,
          medicineName: "Test Medicine",
          quantity: 5,
          quantityUnit: "tablets",
          expiryDate: "2027-01-01",
        })
      );
    });
  });
});