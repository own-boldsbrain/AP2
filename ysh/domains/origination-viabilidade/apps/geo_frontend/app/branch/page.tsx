import { Branch, BranchMessages, BranchNext, BranchPage, BranchPrevious, BranchSelector } from "@/components/ai-elements/branch";

type ConversationMessage = {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
};

type ConversationBranch = {
  id: string;
  label: string;
  summary: string;
  messages: ConversationMessage[];
};

const BRANCHES: ConversationBranch[] = [
  {
    id: "concise-plan",
    label: "Concise plan",
    summary: "High-level roadmap with milestones",
    messages: [
      { role: "user", content: "Can you outline a go-to-market plan for our solar offer?" },
      {
        role: "assistant",
        content:
          "Absolutely! Here's a concise, milestone-based roadmap you can share with the stakeholders."
      },
      {
        role: "assistant",
        content:
          "1. Validate personas and regulatory fit → 2. Launch targeted awareness pilots → 3. Activate co-selling playbooks."
      }
    ]
  },
  {
    id: "detailed-brief",
    label: "Detailed brief",
    summary: "Verbose explanation with context",
    messages: [
      { role: "user", content: "Can you outline a go-to-market plan for our solar offer?" },
      {
        role: "assistant",
        content:
          "Let's go deep: we'll map personas, tariffs, and financing incentives before running a staggered launch."
      },
      {
        role: "assistant",
        content:
          "Phase 1 covers premium residential clusters, Phase 2 extends to SMEs, and Phase 3 activates AP2 upsell offers."
      },
      {
        role: "assistant",
        content:
          "I'll also attach metrics and owners for each phase so product, ops, and finance can align on go-live."
      }
    ]
  },
  {
    id: "experiment",
    label: "Experiment",
    summary: "Hypothesis-driven option",
    messages: [
      { role: "user", content: "Can you outline a go-to-market plan for our solar offer?" },
      {
        role: "assistant",
        content:
          "Proposal: treat this as an experiment. We'll A/B three messaging angles using agent-triggered landings."
      },
      {
        role: "assistant",
        content:
          "Success metric is proposal-to-checkout conversion with AP2-ready bundles; we iterate weekly based on telemetry."
      }
    ]
  }
];

export default function BranchPreviewPage() {
  return (
    <main className="page">
      <section>
        <h1>Branch component</h1>
        <p>
          The Branch component keeps multiple assistant responses in sync so analysts can browse alternative drafts without
          losing context.
        </p>
      </section>

      <Branch defaultBranch={0} className="branch-demo">
        <BranchMessages>
          {BRANCHES.map((branch) => (
            <article key={branch.id} className="branch-thread ysh-gradient-border">
              <header>
                <strong>{branch.label}</strong>
                <span>{branch.summary}</span>
              </header>
              <ul>
                {branch.messages.map((message, index) => (
                  <li key={index} data-role={message.role}>
                    <span className="branch-role">{message.role === "assistant" ? "Assistant" : "User"}</span>
                    <p>{message.content}</p>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </BranchMessages>
        <BranchSelector from="assistant">
          <BranchPrevious />
          <BranchPage />
          <BranchNext />
        </BranchSelector>
      </Branch>
    </main>
  );
}
