import { Car } from "@/domain/Car";
import CarCard from "../CarCard";

type CarConfigurationProps = {
  cars: Car[];
};

export default function CarSelection({ cars }: CarConfigurationProps) {
  return (
    <div className="w-full flex flex-col gap-3">
      {cars.map((car) => (
        <CarCard car={car} />
      ))}
    </div>
  );
}
