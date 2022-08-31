// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery is VRFConsumerBaseV2 {
    VRFCoordinatorV2Interface COORDINATOR;
    uint64 s_subscriptionId;
    bytes32 keyHash = 0xd89b2bf150e3b9e13446986e571fb9cab24b13cea0a43ea20a6049a85cc807cc;
    uint256 public randomness;
    uint256 public s_requestId;
    

    AggregatorV3Interface internal priceFeed;



    uint256 public enteranceFeeUsd = 50 * 10**18;
    address[] public players;
    enum lotteryState { CLOSED, OPEN, CALCULATING_WINNER }
    lotteryState public currentState = lotteryState.CLOSED;

    address s_owner;

    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;

    uint256 public fulfillCalledWith;
    address payable public winner;

    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        // uint64 _subscriptionId,
        bytes32 _keyHash,
        uint32 _callbackGasLimit
    ) VRFConsumerBaseV2(_vrfCoordinator) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        // s_subscriptionId = _subscriptionId;
        keyHash = _keyHash;
        callbackGasLimit = _callbackGasLimit;
        s_owner = msg.sender;
    }
    function enter() public payable {
        require(currentState == lotteryState.OPEN, "Cant enter lottery at this time.");
        require(msg.value > getEnteranceFee(), "You need to spend more eth.");
        players.push(msg.sender);
    }
    function getEnteranceFee() public view returns (uint256) {
        (,int256 price,,,) = priceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        return (enteranceFeeUsd * 10**18) / adjustedPrice;
    }
    function requestRandomNumber(uint64 _subId) public returns (uint256) {
        return COORDINATOR.requestRandomWords(
            keyHash,
            _subId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords) internal override {
        fulfillCalledWith = requestId;
        if (s_requestId == requestId) {
            randomness = randomWords[0];

            if (currentState == lotteryState.CALCULATING_WINNER) {
                winner = payable(selectWinner(randomness));
                winner.transfer(address(this).balance);
                currentState = lotteryState.CLOSED;
            }
        }
    }

    function selectWinner(uint256 rand) view internal returns (address) {
        return players[rand % players.length];
    }

    function closeLottery(uint64 _subId) ownerOnly public payable {
        require(currentState == lotteryState.OPEN);
        currentState = lotteryState.CALCULATING_WINNER;
        s_requestId = requestRandomNumber(_subId);
        emit RequestedRandomness(bytes32(s_requestId));
    } 
    function createNewLottery() ownerOnly public {
        require(currentState == lotteryState.CLOSED);
        currentState = lotteryState.OPEN;
    }

    modifier ownerOnly {
        require(s_owner == msg.sender);
        _;
    }
}
