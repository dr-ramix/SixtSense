import { cn } from "@/lib/utils";
import { CSSProperties, HTMLAttributes } from "react";

type BackgroundGradientProps = HTMLAttributes<HTMLDivElement> & {
  borderWidth?: string;
  duration?: string;
};

export function BackgroundGradient({
  className,
  borderWidth = "1px",
  duration = "14s",
  ...props
}: BackgroundGradientProps) {
  return (
    <div
      aria-hidden
      style={
        {
          "--border-width": borderWidth,
          "--duration": duration,
        } as CSSProperties
      }
      className={cn(
        "selected-card-border absolute inset-0 rounded-[inherit]",
        className
      )}
      {...props}
    />
  );
}

export default BackgroundGradient;
