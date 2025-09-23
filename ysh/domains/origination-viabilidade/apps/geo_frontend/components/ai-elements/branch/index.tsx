"use client";

import type { ButtonHTMLAttributes, HTMLAttributes, ReactElement } from "react";
import {
  Children,
  createContext,
  forwardRef,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from "react";
import styles from "./branch.module.css";

function cn(...inputs: Array<string | false | null | undefined>) {
  return inputs.filter(Boolean).join(" ");
}

type MessageRole = "user" | "assistant" | "system" | "tool";

type BranchContextValue = {
  branchIndex: number;
  branchCount: number;
  setBranchCount: (count: number) => void;
  goToBranch: (index: number) => void;
  goToNext: () => void;
  goToPrevious: () => void;
  canGoNext: boolean;
  canGoPrevious: boolean;
};

const BranchContext = createContext<BranchContextValue | null>(null);

type BranchProps = HTMLAttributes<HTMLDivElement> & {
  defaultBranch?: number;
  onBranchChange?: (branchIndex: number) => void;
};

export const Branch = forwardRef<HTMLDivElement, BranchProps>(function Branch(
  { defaultBranch = 0, onBranchChange, className, children, ...props },
  ref
) {
  const [branchCount, setBranchCountState] = useState(0);
  const [branchIndex, setBranchIndex] = useState(() => Math.max(0, defaultBranch));
  const lastReported = useRef<number | null>(null);

  const setBranchCount = useCallback((count: number) => {
    setBranchCountState((previous) => (previous === count ? previous : count));
  }, []);

  const goToBranch = useCallback(
    (index: number) => {
      setBranchIndex((previous) => {
        if (branchCount === 0) {
          return 0;
        }
        const clamped = Math.min(Math.max(index, 0), branchCount - 1);
        return clamped;
      });
    },
    [branchCount]
  );

  const goToNext = useCallback(() => {
    setBranchIndex((previous) => {
      if (branchCount === 0) {
        return 0;
      }
      return Math.min(previous + 1, branchCount - 1);
    });
  }, [branchCount]);

  const goToPrevious = useCallback(() => {
    setBranchIndex((previous) => {
      if (branchCount === 0) {
        return 0;
      }
      return Math.max(previous - 1, 0);
    });
  }, [branchCount]);

  useEffect(() => {
    setBranchIndex((previous) => {
      if (branchCount === 0) {
        return 0;
      }
      const clamped = Math.min(Math.max(previous, 0), branchCount - 1);
      return clamped;
    });
  }, [branchCount]);

  useEffect(() => {
    setBranchIndex((previous) => {
      if (branchCount === 0) {
        return 0;
      }
      const normalizedDefault = Math.min(Math.max(defaultBranch, 0), branchCount - 1);
      if (normalizedDefault !== previous) {
        return normalizedDefault;
      }
      return previous;
    });
  }, [defaultBranch, branchCount]);

  useEffect(() => {
    if (!onBranchChange) {
      return;
    }
    if (lastReported.current !== branchIndex) {
      lastReported.current = branchIndex;
      onBranchChange(branchIndex);
    }
  }, [branchIndex, onBranchChange]);

  const value = useMemo<BranchContextValue>(() => {
    const canGoPrevious = branchCount > 0 && branchIndex > 0;
    const canGoNext = branchCount > 0 && branchIndex < branchCount - 1;

    return {
      branchIndex,
      branchCount,
      setBranchCount,
      goToBranch,
      goToNext,
      goToPrevious,
      canGoNext,
      canGoPrevious
    };
  }, [branchCount, branchIndex, goToBranch, goToNext, goToPrevious, setBranchCount]);

  return (
    <BranchContext.Provider value={value}>
      <div
        ref={ref}
        className={cn(styles.root, className)}
        data-branch-count={branchCount}
        data-branch-index={branchIndex}
        {...props}
      >
        {children}
      </div>
    </BranchContext.Provider>
  );
});

function useBranchContext(component: string) {
  const context = useContext(BranchContext);
  if (!context) {
    throw new Error(`${component} must be used within <Branch />`);
  }
  return context;
}

export function useBranch() {
  return useBranchContext("useBranch");
}

type BranchMessagesProps = HTMLAttributes<HTMLDivElement>;

export const BranchMessages = forwardRef<HTMLDivElement, BranchMessagesProps>(function BranchMessages(
  { className, children, ...props },
  ref
) {
  const { branchIndex, setBranchCount } = useBranchContext("BranchMessages");
  const childArray = useMemo(() => Children.toArray(children), [children]);
  const childCount = childArray.length;

  useEffect(() => {
    setBranchCount(childCount);
  }, [childCount, setBranchCount]);

  return (
    <div ref={ref} className={cn(styles.messages, className)} {...props}>
      {childArray.map((child, index) => {
        const key = (child as ReactElement)?.key ?? index;
        const isActive = index === branchIndex;
        return (
          <div
            key={key}
            className={styles.slot}
            data-hidden={isActive ? "false" : "true"}
            data-branch-index={index}
            aria-hidden={isActive ? undefined : "true"}
          >
            {child}
          </div>
        );
      })}
    </div>
  );
});

type BranchSelectorProps = HTMLAttributes<HTMLDivElement> & {
  from?: MessageRole;
};

export const BranchSelector = forwardRef<HTMLDivElement, BranchSelectorProps>(function BranchSelector(
  { from = "assistant", className, children, ...props },
  ref
) {
  const { branchCount } = useBranchContext("BranchSelector");

  return (
    <div
      ref={ref}
      className={cn(styles.selector, className)}
      data-role={from}
      data-has-multiple={branchCount > 1}
      {...props}
    >
      {children}
    </div>
  );
});

type BranchButtonProps = ButtonHTMLAttributes<HTMLButtonElement>;

export const BranchPrevious = forwardRef<HTMLButtonElement, BranchButtonProps>(function BranchPrevious(
  { className, children, disabled, onClick, ...props },
  ref
) {
  const { canGoPrevious, goToPrevious } = useBranchContext("BranchPrevious");
  const ariaLabel = props["aria-label"] ?? "Previous branch";
  const { ["aria-label"]: _ariaLabel, ...rest } = props;
  const isDisabled = disabled ?? !canGoPrevious;

  return (
    <button
      ref={ref}
      type="button"
      className={cn(styles.button, className)}
      disabled={isDisabled}
      onClick={(event) => {
        if (onClick) {
          onClick(event);
        }
        if (!event.defaultPrevented && !isDisabled) {
          goToPrevious();
        }
      }}
      aria-label={ariaLabel}
      {...rest}
    >
      {children ?? <span aria-hidden="true">←</span>}
    </button>
  );
});

export const BranchNext = forwardRef<HTMLButtonElement, BranchButtonProps>(function BranchNext(
  { className, children, disabled, onClick, ...props },
  ref
) {
  const { canGoNext, goToNext } = useBranchContext("BranchNext");
  const ariaLabel = props["aria-label"] ?? "Next branch";
  const { ["aria-label"]: _ariaLabel, ...rest } = props;
  const isDisabled = disabled ?? !canGoNext;

  return (
    <button
      ref={ref}
      type="button"
      className={cn(styles.button, className)}
      disabled={isDisabled}
      onClick={(event) => {
        if (onClick) {
          onClick(event);
        }
        if (!event.defaultPrevented && !isDisabled) {
          goToNext();
        }
      }}
      aria-label={ariaLabel}
      {...rest}
    >
      {children ?? <span aria-hidden="true">→</span>}
    </button>
  );
});

type BranchPageProps = HTMLAttributes<HTMLSpanElement>;

export const BranchPage = forwardRef<HTMLSpanElement, BranchPageProps>(function BranchPage(
  { className, children, ...props },
  ref
) {
  const { branchIndex, branchCount } = useBranchContext("BranchPage");
  const defaultLabel = branchCount > 0 ? `${branchIndex + 1} of ${branchCount}` : "0 of 0";

  return (
    <span
      ref={ref}
      className={cn(styles.page, className)}
      aria-live="polite"
      {...props}
    >
      {children ?? defaultLabel}
    </span>
  );
});

export type { BranchProps, BranchMessagesProps, BranchSelectorProps };
export type { MessageRole as BranchSelectorRole };
