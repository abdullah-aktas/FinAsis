// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SampleContract {
    string public message;
    address public owner;

    constructor(string memory _message) {
        message = _message;
        owner = msg.sender;
    }

    function setMessage(string memory _newMessage) public {
        require(msg.sender == owner, "Sadece sahibi değiştirebilir.");
        message = _newMessage;
    }
} 