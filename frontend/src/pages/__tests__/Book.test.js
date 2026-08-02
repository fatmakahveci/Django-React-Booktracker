import axios from "axios";
import { fetchFinishedList } from "../Book";

vi.mock("axios");

const contextValues = {
  user: "",
  authTokens: "token",
  loginUser: "",
  registerUser: "",
  logoutUser: "",
  message: "",
  showMessage: "",
};

vi.mock("react", async () => {
  const ActualReact = await vi.importActual("react");
  return {
    ...ActualReact,
    useContext: () => ({ contextValues })
  };
});

describe("get finished books", () => {
  it("should get finished books", async () => {
    const mockedFinishedList = [{ id: 1, title: "Book 1", finished: true }];
    axios.get.mockImplementationOnce(() => Promise.resolve(mockedFinishedList));
    await expect(fetchFinishedList()).resolves.toEqual(mockedFinishedList);
  });
});
