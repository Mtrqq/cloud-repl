import Prism from "prismjs/components/prism-core";
import "prismjs/components/prism-python";
import "prismjs/components/prism-rust";
import boilerplate from "./boilerplate";

const config = {
  api: {
    url: process.env.API_URL || "ws://0.0.0.0:8025",
    token: process.env.API_TOKEN || "MOCK",
    reconnect: {
      interval: 5000,
      attempts: 100,
    },
  },
  languages: {
    supported: ["python", "rust"],
    grammar: {
      python: Prism.languages["python"],
      rust: Prism.languages["rust"],
    },
    boilerplate: {
      python: boilerplate.python,
      rust: boilerplate.rust,
    },
  },
};

export default config;
