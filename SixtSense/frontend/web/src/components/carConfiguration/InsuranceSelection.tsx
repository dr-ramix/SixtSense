import { Protection } from "@/domain/Protection";
import { Star } from "lucide-react";
import CoverageItemDetails from "./CoverageItemComponent";
import { Card } from "../ui/card";
import BackgroundGradient from "../ui/background-gradient";
import { ScrollArea } from "@radix-ui/react-scroll-area";

type IncuranceSelectionProps = {
  protections: Protection[];
  selectedProtection?: Protection | null;
  onSelect: (protection: Protection) => void;
};

export default function InsuranceSelection({
  protections,
  selectedProtection,
  onSelect,
}: IncuranceSelectionProps) {
  return (
    <ScrollArea className="h-[600px] pr-2">
      <div className="w-full flex flex-col gap-3">
        {protections.map((protection) => {
          const isSelected = selectedProtection?.id === protection.id;
          return (
            <Card
              key={protection.id}
              className={`relative w-full m-0 p-4 h-40 flex flex-1 flex-row items-center justify-start rounded-2xl shadow-md overflow-hidden border transition cursor-pointer ${
                isSelected
                  ? "border-border/70 bg-primary/5"
                  : "border-border/70 hover:border-primary/60 hover:ring-1 hover:ring-primary/20"
              }`}
              onClick={() => onSelect(protection)}
              role="button"
              tabIndex={0}
            >
              {isSelected && <BackgroundGradient />}

              {(() => {
                const hasIncludes = protection.includes.length > 0;
                const hasExcludes = protection.excludes.length > 0;
                const twoColumns = hasIncludes && hasExcludes;

                return (
                  <div
                    className={`
                      relative z-10 grid gap-x-4 gap-y-1 text-sm w-full
                      justify-items-center text-center
                      ${twoColumns ? "grid-cols-2" : "grid-cols-1"}
                    `}
                  >
                    {/* Row 1 */}
                    <div className="font-semibold justify-self-start">
                      {protection.name}
                    </div>
                    <div className="font-large font-bold justify-self-end pr-4 flex items-center gap-1">
                      {[...Array(protection.ratingStars)].map((_, i) => (
                        <Star
                          key={i}
                          className="inline-block w-4 h-4 opacity-70"
                        />
                      ))}
                    </div>

                    {/* Excludes */}
                    <div className={twoColumns ? "" : "col-span-2"}>
                      {hasExcludes && <div>Excludes:</div>}
                      {protection.excludes.map((exclude) => (
                        <CoverageItemDetails key={exclude.id} item={exclude} />
                      ))}
                    </div>

                    {/* Includes */}
                    <div className={twoColumns ? "" : "col-span-2"}>
                      {hasIncludes && <div>Includes:</div>}
                      {protection.includes.map((include) => (
                        <CoverageItemDetails key={include.id} item={include} />
                      ))}
                    </div>

                    {/* Price */}
                    <div className="font-large font-bold justify-self-end col-span-2 pr-4">
                      {protection.price.totalPrice.currency}{" "}
                      {protection.price.totalPrice.amount}
                      {protection.price.totalPrice.suffix}
                    </div>
                  </div>
                );
              })()}
            </Card>
          );
        })}
      </div>
    </ScrollArea>
  );
}
