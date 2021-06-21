package com.example.vaibhav.byob.utils.sqlObject;

import com.example.vaibhav.byob.utils.SharedResources;
import com.example.vaibhav.byob.utils.execution.variables.ExecutionVariables;

import java.util.UUID;

public class UserTableObject {
    
    private UUID uuid;
    private long accountId;
    private String username;
    private String password;
    private long createdAtEpoch;
    
    public UserTableObject(String username, String password) {
        
        this.uuid = SharedResources.generateUUID();
        this.accountId = SharedResources.getRandom10Digits();
        this.username = username;
        this.password = password;
        this.createdAtEpoch = System.currentTimeMillis();
        
        ExecutionVariables.uuid = this.uuid;
        ExecutionVariables.accountId = this.accountId;
        ExecutionVariables.username = this.username;
        
        
    }
    
    public long getAccountId() {
        return accountId;
    }
    
    public void setAccountId(long accountId) {
        this.accountId = accountId;
    }
    
    public UUID getUuid() {
        return uuid;
    }
    
    public void setUuid(UUID uuid) {
        this.uuid = uuid;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public long getCreatedAtEpoch() {
        return createdAtEpoch;
    }
    
    public void setCreatedAtEpoch(long createdAtEpoch) {
        this.createdAtEpoch = createdAtEpoch;
    }
    
    
}
