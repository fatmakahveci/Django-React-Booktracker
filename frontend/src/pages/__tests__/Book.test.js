import axios from "axios";
import { fetchFinishedList } from "../Book";

jest.mock("axios");

const contextValues = {
  user: "",
  authTokens: "token",
  loginUser: "",
  registerUser: "",
  logoutUser: "",
  message: "",
  showMessage: "",
};

jest.mock("react", () => {
  const ActualReact = jest.requireActual("react");
  return {
    ...ActualReact,
    useContext: () => ({ contextValues })
  };
});

describe("get finished books", () => {
  it("should get finished books", async () => {
    const mockedFinishedList = [{ id: 1, title: "Book 1", finished: true }];
    axios.get.mockImplementationOnce(() => Promise.resolve(mockedFinishedList));
    fetchFinishedList();
    // await expect(finishedList).resolves.toEqual(mockedFinishedList);
  });
});
