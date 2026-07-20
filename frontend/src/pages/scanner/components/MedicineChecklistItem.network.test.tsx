import { render, screen, fireEvent } from "@testing-library/react";
import MedicineChecklistItem from "./MedicineChecklistItem";

const mockMedicine = {
  medicineId: 123,
  name: "Test Medicine",
  genericName: "Test Generic",
  brandName: "Test Brand",
  type: "tablet",
};

const baseProps = {
  id: "row-netfail",
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

describe("MedicineChecklistItem - network failure", () => {
  it("displays error when onSubmit fails", async () => {
    const errorPromise = Promise.reject(new Error("Network error"));
    const onSubmit = jest.fn().mockReturnValue(errorPromise);
    render(<MedicineChecklistItem {...baseProps, onSubmit} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    // Wait for error message to appear
    expect(screen.getByText(/submission failed/i)).toBeInTheDocument();
    expect(onSubmit).toHaveBeenCalled();
  });
});