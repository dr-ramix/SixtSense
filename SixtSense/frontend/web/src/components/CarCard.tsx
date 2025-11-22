import { Car } from "@/domain/Car";
import { Card } from "./ui/card";
import CarDetails from "./CarDetails";

type CarCardProps = { car: Car };

export default function CarCard({ car }: CarCardProps) {
  const { vehicle } = car;
  const imageUrl = vehicle.images[0];

  return (
    <Card className="w-full m-0 p-0 h-40 flex flex-1 flex-row items-center justify-start rounded-2xl shadow-md overflow-hidden">
      <div className="relative h-full w-2/5 flex items-center justify-start object-contain">
        <div
          className="absolute inset-0 rounded-l-2xl bg-[url('https://img.sixt.com/1600/6f09b0e8-6820-4ac0-bedd-5797e9814c18.jpg')] bg-cover bg-center opacity-30 flex-shrink-0 overflow-hidden"
          aria-hidden="true"
        />
        <img
          src={imageUrl}
          alt={`${vehicle.brand} ${vehicle.model}`}
          className="relative z-10 h-[160px] object-cover"
        />
      </div>
      <CarDetails car={car} />
    </Card>
  );
}
