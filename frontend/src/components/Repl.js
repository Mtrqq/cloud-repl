import {
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from "@material-ui/core";
import Autocomplete from "@material-ui/lab/Autocomplete";
import NotInterestedIcon from "@material-ui/icons/NotInterested";
import CancelIcon from "@material-ui/icons/Cancel";
import CheckCircleIcon from "@material-ui/icons/CheckCircle";
import { Fragment, useState, useCallback } from "react";
import { highlight } from "prismjs";
import Editor from "react-simple-code-editor";
import config from "../config";
import useWebSocket from "react-use-websocket";
import { Beforeunload } from "react-beforeunload";

const ExecutionStatus = Object.freeze({
  INACTIVE: 1,
  RUNNING: 2,
  CRASHED: 3,
  FINISHED: 4,
  FAILED: 5,
});

const emptyExecution = () => {
  return {
    status: ExecutionStatus.INACTIVE,
    exitCode: null,
    stagesCount: null,
    currentStage: null,
    currentStageIndex: null,
    stdout: {},
  };
};

const createMessageDispatcher = (setExecution) => {
  return (event) => {
    const message = JSON.parse(event.data);
    console.log("GOT MESSAGE FROM SERVER", message);
    if (message.type == "ExecutionStartedResponse") {
      setExecution((prevState) => ({
        ...prevState,
        status: ExecutionStatus.RUNNING,
        stagesCount: message.stages,
        currentStageIndex: 0,
      }));
    } else if (message.type == "StageStartedNotification") {
      setExecution((prevState) => ({
        ...prevState,
        currentStage: message.stage,
        currentStageIndex: prevState.currentStageIndex + 1,
      }));
    } else if (message.type == "ExecutionFinishedNotification") {
      const status = message.succeeded
        ? ExecutionStatus.FINISHED
        : ExecutionStatus.FAILED;
      setExecution((prevState) => ({
        ...prevState,
        status,
        exitCode: message["exit_code"],
      }));
    } else if (message.type == "ExecutionOutputNotification") {
      setExecution((prevState) => {
        var stdout = prevState.stdout[message.stage] || "";
        stdout = stdout.concat(message.output);

        return {
          ...prevState,
          stdout: { ...prevState.stdout, [message.stage]: stdout },
        };
      });
    } else if (message.type == "ExecutionFailedResponse") {
      console.log("SERVER ERROR: ", message.detail);
      console.log("TRACEBACK", message.traceback);
      setExecution((prevState) => ({
        ...prevState,
        status: ExecutionStatus.CRASHED,
      }));
    }
  };
};

function getSocketUrlForLang(lang) {
  return `ws://${window.location.hostname}/api/${lang}`;
}

function Repl() {
  const [state, setState] = useState({
    code: "",
    lang: config.languages.supported[0],
    connected: false,
  });
  const [execution, setExecution] = useState(emptyExecution);

  const getSocketUrl = useCallback(() => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(getSocketUrlForLang(state.lang));
      }, 2000);
    });
  }, [state.lang]);

  const { sendJsonMessage } = useWebSocket(getSocketUrl, {
    onOpen: (event) => {
      console.log("Connected to ", event.currentTarget.url);
      setState((prevState) => {
        return { ...prevState, connected: true };
      });
    },
    onClose: (event) => {
      console.log("Connection to ", event.currentTarget.url + " closed");
      setState((prevState) => {
        return { ...prevState, connected: false };
      });
    },
    onMessage: createMessageDispatcher(setExecution),
    reconnectInterval: config.api.reconnect.interval,
    reconnectAttempts: config.api.reconnect.attempts,
    shouldReconnect: (_) => true,
    share: true,
  });

  const handler = () => {
    sendJsonMessage({ code: state.code });
  };

  return (
    <Fragment>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          columnGap: "50px",
          height: "100vh",
          width: "100%",
        }}
      >
        <Autocomplete
          style={{
            width: "30%",
          }}
          id="languageSelector"
          options={config.languages.supported}
          value={state.lang}
          onChange={(_, lang) =>
            setState((prevState) => {
              return { ...prevState, lang };
            })
          }
          renderInput={(params) => <TextField {...params} label="Language" />}
          disableClearable={true}
        />
        <Editor
          value={state.code}
          tabSize={4}
          onValueChange={(code) =>
            setState((prevState) => {
              return { ...prevState, code };
            })
          }
          highlight={(code) =>
            highlight(code, config.languages.grammar[state.lang])
          }
          padding={10}
          style={{
            fontFamily: '"Fira code", "Fira Mono", monospace',
            fontSize: 12,
            width: "45%",
            height: "50%",
            outline: "1px solid black",
            margin: "50px",
            fontVariantLigatures: "common-ligatures",
            backgroundColor: "#fafafa",
            borderRadius: "3px",
          }}
        />
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-around",
            width: "45%",
          }}
        >
          <Button
            style={{
              width: "30%",
              backgroundColor: "#1362ab",
              color: "white",
              disabled: { backgroundColor: "#ffffff" },
            }}
            onClick={handler}
            variant="contained"
            disabled={!state.connected}
          >
            Run
          </Button>
          <Button
            style={{
              width: "30%",
              backgroundColor: "#1362ab",
              color: "white",
            }}
            onClick={() =>
              setState((prevState) => ({ ...prevState, code: "" }))
            }
            variant="contained"
          >
            Clear
          </Button>
          <Button
            style={{
              width: "30%",
              backgroundColor: "#1362ab",
              color: "white",
            }}
            onClick={() => {
              setState((prevState) => ({
                ...prevState,
                code: config.languages.boilerplate[state.lang],
              }));
            }}
            variant="contained"
          >
            Boilerplate
          </Button>
        </div>
      </div>
      <Dialog
        open={execution.status != ExecutionStatus.INACTIVE}
        maxWidth="sm"
        fullWidth={true}
        keepMounted
      >
        <DialogTitle>{"Evaluation progress"}</DialogTitle>
        <DialogContent>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <TextField
              fullWidth={true}
              style={{ marginBottom: 30 }}
              value={execution.stdout[execution.currentStage] || ""}
              inputProps={{
                readOnly: true,
                disabled: true,
              }}
              multiline
              minRows={15}
              maxRows={15}
              variant="outlined"
            />
            {execution.status == ExecutionStatus.RUNNING && (
              <CircularProgress />
            )}
            {execution.status == ExecutionStatus.CRASHED && (
              <NotInterestedIcon fontSize="large" />
            )}
            {execution.status == ExecutionStatus.FAILED && (
              <CancelIcon fontSize="large" />
            )}
            {execution.status == ExecutionStatus.FINISHED && (
              <CheckCircleIcon fontSize="large" />
            )}
          </div>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setExecution(emptyExecution());
            }}
            disabled={execution.status == ExecutionStatus.RUNNING}
            color="primary"
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
      <Beforeunload onBeforeunload={() => "You’ll lose your data!"} />
    </Fragment>
  );
}

export default Repl;
