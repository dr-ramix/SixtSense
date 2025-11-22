import { Car } from "@/domain/Car";
import CarCard from "../CarCard";

type CarConfigurationProps = {
  cars: Car[];
  selectedCar?: Car | null;
  onSelect: (car: Car) => void;
};

export default function CarSelection({
  cars,
  selectedCar,
  onSelect,
}: CarConfigurationProps) {
  return (
    <div className="w-full flex flex-col gap-3">
      {cars.map((car) => (
        <CarCard
          key={car.vehicle.id}
          car={car}
          selected={selectedCar?.vehicle.id === car.vehicle.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
