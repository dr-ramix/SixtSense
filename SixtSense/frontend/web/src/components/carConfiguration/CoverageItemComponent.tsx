import { CoverageItem } from "@/domain/Protection";
import { Info } from "lucide-react";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";

type CoberageItemProps = {
  item: CoverageItem;
};

export default function CoverageItemDetails({ item }: CoberageItemProps) {
  return (
    <div className="w-full flex flex-col gap-3">
      <div className="flex items-center gap-1">
        <div className="flex flex-col align-top justify-start">
          {item.title}
        </div>

        <Tooltip>
          <TooltipTrigger asChild>
            <Info className="inline-block w-3 h-3 opacity-50 ml-1 cursor-pointer" />
          </TooltipTrigger>
          <TooltipContent className="max-w-xs">
            <p>{item.description}</p>
          </TooltipContent>
        </Tooltip>
      </div>

      <div>
        {item.tags.map((tag) => (
          <span
            key={tag}
            className="bg-gray-200 text-gray-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full dark:bg-gray-700 dark:text-gray-300"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
