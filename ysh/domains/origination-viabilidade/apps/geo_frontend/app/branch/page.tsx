"use client";

import { useState, type ReactNode } from "react";
import {
  Branch,
  BranchMessages,
  BranchNext,
  BranchPage,
  BranchPrevious,
  BranchSelector,
} from "@/components/ai-elements/branch";
import "./branch-demo.css";

type DemoMessage = {
  id: string;
  from: "user" | "assistant" | "system";
  author?: string;
  content: string;
};

type DemoBranch = {
  id: string;
  title: string;
  summary: string;
  messages: DemoMessage[];
};

const DEMO_BRANCHES: DemoBranch[] = [
  {
    id: "solar-storage",
    title: "Plano A · Solar + Bateria",
    summary:
      "O agente recomenda um sistema fotovoltaico de 9.8kW com bateria de 10kWh para cobrir 92% do consumo anual e maximizar o uso de energia fora do horário de ponta.",
    messages: [
      {
        id: "user-0",
        from: "user",
        author: "Cliente",
        content: "Quero reduzir a conta de energia e ter backup em caso de apagões."
      },
      {
        id: "assistant-0",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Analisei seu histórico de consumo e recomendo um sistema de 9.8kW com 12 painéis bifaciais. Acrescente uma bateria de 10kWh para cobrir os apagões de até 6 horas."
      },
      {
        id: "assistant-1",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Com os incentivos vigentes, o payback estimado é de 4.2 anos e a economia anual supera R$ 6.300."
      },
      {
        id: "user-1",
        from: "user",
        author: "Cliente",
        content: "Consigo acompanhar a carga da bateria pelo app?"
      },
      {
        id: "assistant-2",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Sim! O app mostra o fluxo de energia em tempo real e envia alertas quando a bateria chega a 20% para preservar o backup."
      }
    ]
  },
  {
    id: "solar-no-storage",
    title: "Plano B · Solar Essencial",
    summary:
      "Alternativa sem bateria, priorizando o menor custo inicial com 86% de cobertura do consumo anual.",
    messages: [
      {
        id: "user-0",
        from: "user",
        author: "Cliente",
        content: "Talvez eu não precise de bateria, quero saber o custo mínimo."
      },
      {
        id: "assistant-0",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Neste cenário, proponho um sistema de 8.2kW com inversor híbrido pronto para adicionar baterias no futuro."
      },
      {
        id: "assistant-1",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "O investimento inicial cai 28% em relação ao plano A, com payback estimado em 3.7 anos."
      },
      {
        id: "user-1",
        from: "user",
        author: "Cliente",
        content: "E como ficam as contas no horário de ponta?"
      },
      {
        id: "assistant-2",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Durante ponta você ainda importa energia, mas o excedente gerado durante o dia compensa 76% do custo adicional."
      }
    ]
  },
  {
    id: "finance-focused",
    title: "Plano C · Foco Financeiro",
    summary:
      "Ajusta o número de painéis para otimizar o fluxo de caixa, mantendo payback inferior a 5 anos e parcela mensal abaixo de R$ 780.",
    messages: [
      {
        id: "user-0",
        from: "user",
        author: "Cliente",
        content: "Quero financiar sem aumentar minha parcela mensal além de R$ 800."
      },
      {
        id: "assistant-0",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Montei um kit de 7.4kW com financiamento de 72 meses. A parcela fica em R$ 768, compensada pela economia média de R$ 690."
      },
      {
        id: "assistant-1",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Configurei alertas automáticos: se a economia cair 10% em qualquer mês, o agente agenda uma inspeção remota."
      },
      {
        id: "user-1",
        from: "user",
        author: "Cliente",
        content: "Isso inclui suporte para limpeza dos painéis?"
      },
      {
        id: "assistant-2",
        from: "assistant",
        author: "Solar Copilot",
        content:
          "Sim, o plano de serviço cobre duas limpezas anuais e monitoramento proativo do desempenho via sensores IoT."
      }
    ]
  }
];

type MessageProps = {
  from: DemoMessage["from"];
  author?: string;
  children: ReactNode;
};

function Message({ from, author, children }: MessageProps) {
  return (
    <article className={`branch-demo__message branch-demo__message--${from}`}>
      <div className="branch-demo__avatar" aria-hidden="true">
        {from === "assistant" ? "🤖" : from === "system" ? "⚙️" : "🧑"}
      </div>
      <div className="branch-demo__bubble">
        {author ? <header className="branch-demo__author">{author}</header> : null}
        <div className="branch-demo__content">{children}</div>
      </div>
    </article>
  );
}

function MessageContent({ children }: { children: ReactNode }) {
  return <p className="branch-demo__text">{children}</p>;
}

export default function BranchPreviewPage() {
  const [activeBranch, setActiveBranch] = useState(0);
  const active = DEMO_BRANCHES[activeBranch] ?? DEMO_BRANCHES[0];

  return (
    <main className="branch-demo">
      <section className="branch-demo__intro">
        <h1>Branch · Visualizador de respostas alternativas</h1>
        <p>
          Navegue entre ramificações de mensagens geradas pelo agente. Use as setas ou o teclado para comparar respostas antes de selecionar a melhor opção para o cliente.
        </p>
        <dl className="branch-demo__summary">
          <div>
            <dt>Ramificação ativa</dt>
            <dd>{active.title}</dd>
          </div>
          <div>
            <dt>Resumo</dt>
            <dd>{active.summary}</dd>
          </div>
        </dl>
      </section>

      <Branch
        defaultBranch={0}
        onBranchChange={(index) => setActiveBranch(index)}
        className="branch-demo__widget"
      >
        <BranchMessages>
          {DEMO_BRANCHES.map((branch) => (
            <div key={branch.id} className="branch-demo__thread">
              <span className="branch-demo__pill">{branch.title}</span>
              {branch.messages.map((message) => (
                <Message key={message.id} from={message.from} author={message.author}>
                  <MessageContent>{message.content}</MessageContent>
                </Message>
              ))}
            </div>
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
