"use client";

import {
  Children,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type KeyboardEvent,
  type MouseEvent,
  type ReactElement,
  type ReactNode,
  forwardRef,
} from "react";
import "./branch.css";

function cx(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

type MessageRole = "user" | "assistant" | "system" | (string & {});

type BranchContextValue = {
  branchIndex: number;
  branchCount: number;
  canGoNext: boolean;
  canGoPrevious: boolean;
  goToBranch: (index: number) => void;
  goToNext: () => void;
  goToPrevious: () => void;
  updateBranchCount: (count: number) => void;
};

const BranchContext = createContext<BranchContextValue | null>(null);

function useBranchContext(component: string): BranchContextValue {
  const context = useContext(BranchContext);

  if (!context) {
    throw new Error(`${component} must be used within a <Branch /> component.`);
  }

  return context;
}

const clamp = (value: number, min: number, max: number): number => {
  if (max < min) {
    return min;
  }

  return Math.min(Math.max(value, min), max);
};

type BranchProps = {
  defaultBranch?: number;
  onBranchChange?: (branchIndex: number) => void;
  children: ReactNode;
} & React.HTMLAttributes<HTMLDivElement>;

export function Branch({
  defaultBranch = 0,
  onBranchChange,
  children,
  className,
  onKeyDown,
  tabIndex,
  ...props
}: BranchProps): ReactElement {
  const [branchIndex, setBranchIndex] = useState(defaultBranch);
  const [branchCount, setBranchCount] = useState(0);

  useEffect(() => {
    setBranchIndex((previous) => clamp(previous, 0, Math.max(branchCount - 1, 0)));
  }, [branchCount]);

  useEffect(() => {
    if (branchCount === 0) {
      return;
    }

    onBranchChange?.(branchIndex);
  }, [branchIndex, branchCount, onBranchChange]);

  const goToBranch = useCallback(
    (index: number) => {
      setBranchIndex(() => clamp(index, 0, Math.max(branchCount - 1, 0)));
    },
    [branchCount]
  );

  const goToNext = useCallback(() => {
    setBranchIndex((previous) => clamp(previous + 1, 0, Math.max(branchCount - 1, 0)));
  }, [branchCount]);

  const goToPrevious = useCallback(() => {
    setBranchIndex((previous) => clamp(previous - 1, 0, Math.max(branchCount - 1, 0)));
  }, [branchCount]);

  const updateBranchCount = useCallback((count: number) => {
    setBranchCount((previous) => (previous === count ? previous : count));
  }, []);

  const canGoPrevious = branchCount > 0 && branchIndex > 0;
  const canGoNext = branchCount > 0 && branchIndex < branchCount - 1;

  const contextValue = useMemo<BranchContextValue>(
    () => ({
      branchIndex,
      branchCount,
      canGoNext,
      canGoPrevious,
      goToBranch,
      goToNext,
      goToPrevious,
      updateBranchCount,
    }),
    [
      branchIndex,
      branchCount,
      canGoNext,
      canGoPrevious,
      goToBranch,
      goToNext,
      goToPrevious,
      updateBranchCount,
    ]
  );

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>) => {
      onKeyDown?.(event);

      if (event.defaultPrevented) {
        return;
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();
        goToNext();
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        goToPrevious();
      }
    },
    [goToNext, goToPrevious, onKeyDown]
  );

  const resolvedTabIndex = tabIndex ?? 0;

  return (
    <BranchContext.Provider value={contextValue}>
      <div
        {...props}
        role="group"
        tabIndex={resolvedTabIndex}
        onKeyDown={handleKeyDown}
        className={cx("branch", className)}
        data-branch-index={branchIndex}
        data-branch-count={branchCount}
      >
        {children}
      </div>
    </BranchContext.Provider>
  );
}

type BranchMessagesProps = {
  children: ReactNode;
} & React.HTMLAttributes<HTMLDivElement>;

export function BranchMessages({ children, className, ...props }: BranchMessagesProps): ReactElement {
  const { branchIndex, updateBranchCount } = useBranchContext("BranchMessages");
  const panels = useMemo(() => Children.toArray(children), [children]);
  const panelCount = panels.length;

  useEffect(() => {
    updateBranchCount(panelCount);
  }, [panelCount, updateBranchCount]);

  return (
    <div
      {...props}
      className={cx("branch__messages", className)}
      data-panel-count={panelCount}
      role="presentation"
    >
      {panels.map((panel, index) => (
        <div
          key={index}
          className={cx(
            "branch__panel",
            index === branchIndex ? "branch__panel--active" : "branch__panel--inactive"
          )}
          role="tabpanel"
          aria-hidden={index !== branchIndex}
          data-state={index === branchIndex ? "active" : "inactive"}
          data-branch-panel-index={index}
        >
          {panel}
        </div>
      ))}
    </div>
  );
}

type BranchSelectorProps = {
  from?: MessageRole;
} & React.HTMLAttributes<HTMLDivElement>;

export function BranchSelector({ from = "assistant", className, ...props }: BranchSelectorProps): ReactElement {
  return (
    <div
      {...props}
      className={cx("branch__selector", `branch__selector--${from}`, className)}
      data-role={from}
      role="toolbar"
      aria-label="Branch navigation"
    />
  );
}

type BranchButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

type BranchButtonComponent = (props: BranchButtonProps) => ReactElement;

const BranchButton = (
  direction: "previous" | "next",
  action: (context: BranchContextValue) => void,
  isDisabled: (context: BranchContextValue) => boolean
): BranchButtonComponent => {
  const Component = forwardRef<HTMLButtonElement, BranchButtonProps>(function BranchButtonImpl(
    { className, onClick, disabled, ...props },
    ref
  ) {
    const context = useBranchContext(direction === "previous" ? "BranchPrevious" : "BranchNext");
    const computedDisabled = disabled ?? isDisabled(context);

    const handleClick = useCallback(
      (event: MouseEvent<HTMLButtonElement>) => {
        onClick?.(event);

        if (event.defaultPrevented || computedDisabled) {
          return;
        }

        action(context);
      },
      [computedDisabled, context, onClick]
    );

    const fallbackLabel = direction === "previous" ? "←" : "→";

    return (
      <button
        {...props}
        ref={ref}
        type="button"
        className={cx("branch__button", `branch__button--${direction}`, className)}
        onClick={handleClick}
        disabled={computedDisabled}
        aria-label={direction === "previous" ? "Previous branch" : "Next branch"}
        data-state={computedDisabled ? "disabled" : "enabled"}
      >
        {props.children ?? fallbackLabel}
      </button>
    );
  });

  Component.displayName = direction === "previous" ? "BranchPrevious" : "BranchNext";

  return Component;
};

export const BranchPrevious = BranchButton(
  "previous",
  (context) => context.goToPrevious(),
  (context) => !context.canGoPrevious
);

export const BranchNext = BranchButton(
  "next",
  (context) => context.goToNext(),
  (context) => !context.canGoNext
);

type BranchPageProps = React.HTMLAttributes<HTMLSpanElement>;

export const BranchPage = forwardRef<HTMLSpanElement, BranchPageProps>(function BranchPage(
  { className, children, ...props },
  ref
) {
  const { branchIndex, branchCount } = useBranchContext("BranchPage");
  const defaultLabel = branchCount === 0 ? "0 of 0" : `${branchIndex + 1} of ${branchCount}`;

  return (
    <span
      {...props}
      ref={ref}
      className={cx("branch__page", className)}
      aria-live="polite"
      data-branch-index={branchIndex}
      data-branch-count={branchCount}
    >
      {children ?? defaultLabel}
    </span>
  );
});

BranchPage.displayName = "BranchPage";
