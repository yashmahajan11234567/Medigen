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
  id: "row-jwt",
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

describe("MedicineChecklistItem - expired JWT", () => {
  it("displays unauthorized error when onSubmit returns 401", async () => {
    const errorPromise = Promise.reject({ response: { status: 401, data: { error: "Unauthorized" } } });
    const onSubmit = jest.fn().mockReturnValue(errorPromise);
    render(<MedicineChecklistItem {...baseProps, onSubmit} />);
    fireEvent.click(screen.getByRole("button", { name: /add to inventory/i }));
    await screen.findByText(/unauthorized/i);
    expect(screen.getByText(/unauthorized/i)).toBeInTheDocument();
    expect(onSubmit).toHaveBeenCalled();
  });
});