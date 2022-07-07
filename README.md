# decentra-vote
Decentra vote is a decentralized and permissionless smart contract for conducting voting polls.

***DISCLAIMER:*** The source code in this tutorial isn't audited. Usage is purely at the risk of the user of the resulting smart contract code (TEAL).

## Usage
There are three application calls that handle the processes of the voting poll, which are for creation, voting and vote retraction.

### Application Creation
Upon creation of the application, there are three mandatory arguments that are to hold these three global states respectively:

- **poll_title (byteslice):** a string (byteslice) argument that provides the title of the poll. An instance could be where we have a poll to select the fastest land animal "Which of these is the fastest land animal?".

- **poll_start_time (uint64):** an integral argument that provides the timestamp value (UTC) in which the poll should start. Must be greater than the current timestamp.

- **poll_end_time (uint64):** an integral argument that provides the timestamp value (UTC) in which the poll should end. Must be greater than the start time.

- **...options:** Other arguments (limited to 30) that are the options values for the voting. For a poll with the title previously mentioned, we could have arguments appended to the aforementioned as in:

```js
    ["cheetah", "lion", "antelope", "jaguar"]
```
A typical Application creation call would have the following example format:

```js
    application_args = ["Which of these is the fastest animal?", 1657229569, 1657230000, "cheetah", "lion", "antelope", "jaguar"]
```
Make sure to use the right encoding for whichever programming language you are making use of.

In JavaScript, integers and byteslices, for example would be encoded with:

```js
    time = algosdk.encodeUint64(1657229569);
    let enc = new TextEncoder();
    option = enc.encode("cheetah");
```

Upon creation, these values would be stored as global state key-value-pairs.

### OptIn

The opt-in transaction would be an Application OptIn transaction, which would prepare an allocation in the account address. No arguments or extra parameters would be sent for the OptIn Call.

### Application Call (voting) NoOp

To conduct a vote, an application call is to be made with two positional arguments thus:

- vote (byteslice)
- choice (uint64) - To represent the position of the option in the 