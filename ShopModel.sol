
// SPDX-License-Identifier: MIT
pragma solidity >0.8.2;

contract ShopModel{
    ItemNode[] public assortiment;
    
    mapping (address => OrderInfo[]) readyOrders;
    mapping(address => OrderInfo[])  orders;


    struct OrderInfo{
        ItemNode item;
        uint needMoney;
        bool completed;
    }

    struct ItemNode {
        uint price;
        string name;
        uint prepayment;
    }

    function checkDebt(uint id) public view  returns (OrderInfo memory){
        require(id < orders[msg.sender].length);
        return  orders[msg.sender][id];
    }

    function makeItem(uint price, string memory name, uint prepayment) public {
        require(prepayment < price, "Prepayment < price always");
        ShopAddItem(ItemNode(price, name, prepayment));
    }

    function ShopAddItem(ItemNode memory newItem) public {
        assortiment.push(newItem);
    }

    function MakeOrder(uint id) public payable {
        uint prepayment = msg.value;
        require(id < assortiment.length && assortiment[id].prepayment < prepayment && assortiment[id].price >= prepayment );
        ItemNode storage item = assortiment[id];
        if (assortiment[id].price <= prepayment){
            assortiment[id] = assortiment[assortiment.length - 1];
            assortiment.pop();
            OrderInfo memory readyOrderInfo = OrderInfo(item, 0, true); 
            readyOrders[msg.sender].push(readyOrderInfo);
        }
        assortiment[id] = assortiment[assortiment.length - 1];
        OrderInfo memory newOrder = OrderInfo(assortiment[id], assortiment[id].price - prepayment, false);
        orders[msg.sender].push(newOrder);
    }

    function CompleteOrder(uint id) public payable {
        uint payment = msg.value;
        require(id < orders[msg.sender].length);
            orders[msg.sender][id].needMoney -= payment;
        if (orders[msg.sender][id].needMoney > payment){
        }
        if (orders[msg.sender][id].needMoney <= 0){
            orders[msg.sender][id].completed = true;
        }
    }


}