import { Car } from "@/domain/Car";
import { Protection } from "@/domain/Protection";
import { AddOnOption } from "@/domain/AddOn";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type SubmitDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selection: {
    car: Car | null;
    protection: Protection | null;
    addOnOptions: AddOnOption[];
  };
  onFinalize: () => void;
};

export function SubmitDialog({
  open,
  onOpenChange,
  selection,
  onFinalize,
}: SubmitDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Review your booking</DialogTitle>
          <DialogDescription>
            Please confirm the details below before finalising your booking.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 text-sm">
          {/* Car */}
          <div>
            <h3 className="font-semibold mb-1">Car</h3>
            {selection.car ? (
              <p>
                {selection.car.vehicle.brand} {selection.car.vehicle.model} (
                {selection.car.vehicle.groupType}) –{" "}
                {selection.car.pricing.totalPrice.amount}{" "}
                {selection.car.pricing.totalPrice.currency}{" "}
                {selection.car.pricing.totalPrice.suffix}
              </p>
            ) : (
              <p className="text-muted-foreground">No car selected.</p>
            )}
          </div>

          {/* Insurance */}
          <div>
            <h3 className="font-semibold mb-1">Insurance</h3>
            {selection.protection ? (
              <p>{selection.protection.name}</p>
            ) : (
              <p className="text-muted-foreground">No insurance selected.</p>
            )}
          </div>

          {/* Add-ons */}
          <div>
            <h3 className="font-semibold mb-1">Add-ons</h3>
            {selection.addOnOptions.length > 0 ? (
              <ul className="list-disc list-inside space-y-1">
                {selection.addOnOptions.map((opt) => (
                  <li key={opt.chargeDetail.id}>
                    {opt.chargeDetail.title} –{" "}
                    {opt.additionalInfo.price.displayPrice.amount}{" "}
                    {opt.additionalInfo.price.displayPrice.currency}
                    {opt.additionalInfo.price.displayPrice.suffix}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground">No add-ons selected.</p>
            )}
          </div>
        </div>

        <DialogFooter className="flex justify-between sm:justify-between">
          <Button
            variant="outline"
            type="button"
            onClick={() => onOpenChange(false)}
            className="bg-white! border! border-black! text-black!"
          >
            Back to selection
          </Button>
          <Button type="button" onClick={onFinalize}>
            Finalise booking
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
