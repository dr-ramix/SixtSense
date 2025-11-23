import { Car } from "@/domain/Car";
import { Handbag } from "lucide-react";

type CarDetailProps = {
  car: Car;
};

export default function CarDetails({ car }: CarDetailProps) {
  const { vehicle, pricing } = car;
  const seatsAmount = vehicle.attributes.find(
    (attr) => attr.key === "P100_VEHICLE_ATTRIBUTE_SEATS"
  )?.value;
  const seatIcon = "https://www.sixt.com/shared/icons/trex/p100/seat.png";

  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm align-top justify-start">
      {/* Row 1 */}
      <div className="font-semibold justify-self-start">
        {vehicle.brand} {vehicle.model}
      </div>
      <div className="font-large font-bold justify-self-end pr-8">
        {pricing.displayPrice.currency} {pricing.displayPrice.amount}
        {pricing.displayPrice.suffix}
      </div>

      {/* Row 2 */}
      <div className="text-muted-foreground col-span-2 justify-self-start">
        {vehicle.transmissionType}
      </div>

      {/* Row 3 */}
      <div className="flex items-center gap-2">
        <img src={seatIcon} alt="Seats" className="w-4 h-4 opacity-70" />
        <span>{seatsAmount}</span>
      </div>

      <div className="flex items-center gap-2">
        <Handbag className="w-4 h-4 opacity-70" />
        {vehicle.bagsCount}
      </div>

      {/* Row 4 — full width */}
      <div className="col-span-2 text-muted-foreground text-xs mt-2 leading-snug justify-self-start">
        {vehicle.fuelType} - {vehicle.acrissCode} - {vehicle.tyreType} tires
      </div>
    </div>
  );
}
