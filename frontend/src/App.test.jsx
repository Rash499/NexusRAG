import { describe, expect, it } from "vitest";
import { apiService } from "./services/api";

describe("RAG frontend services", () => {
  it("has apiService defined with required methods", () => {
    expect(typeof apiService.query).toBe("function");
    expect(typeof apiService.queryStream).toBe("function");
    expect(typeof apiService.ingestCorpus).toBe("function");
    expect(typeof apiService.directIngest).toBe("function");
    expect(typeof apiService.getSystemStatus).toBe("function");
  });
});

