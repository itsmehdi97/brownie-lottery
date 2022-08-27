// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable{

    AggregatorV3Interface internal priceFeed;
    uint256 public enteranceFeeUsd = 50 * 10**18;
    address[] people;
    enum lotteryState { CLOSED, OPEN, CALCULATING_WINNER }
    lotteryState public currentState = lotteryState.CLOSED;

    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
    }
    function enter() public payable {
        require(currentState == lotteryState.OPEN, "Cant enter lottery at this time.");
        require(msg.value > getEnteranceFee(), "You need to spend more eth.");
        people.push(msg.sender);
    }
    function getEnteranceFee() public view returns (uint256) {
        (,int256 price,,,) = priceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        return (enteranceFeeUsd * 10**18) / adjustedPrice;
    }
    // function closeLottery() public payable {
    //     require(currentState == lotteryState.OPEN);
    //     currentState = lotteryState.CALCULATING_WINNER;

    //     address winner = people[-1];
    //     winner.transfer(address(this).balance);
    //     people = new address[];
    //     currentState = lotteryState.CLOSED;
    // } 
    function createNewLottery() public {
        require(currentState == lotteryState.CLOSED);
        currentState = lotteryState.OPEN;
    }
}