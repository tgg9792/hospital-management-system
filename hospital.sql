DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db;
USE hospital_db;


-- 科室表
CREATE TABLE department (
    dept_id      INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(50) NOT NULL UNIQUE,
    location     VARCHAR(100)
);

-- 医生表
CREATE TABLE doctor (
    doctor_id    INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(20) NOT NULL,
    gender       ENUM('男','女'),
    title        VARCHAR(20) COMMENT '职称：主任医师/副主任医师/主治医师等',
    phone        VARCHAR(20),
    dept_id      INT NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE RESTRICT
);

-- 病人表
CREATE TABLE patient (
    patient_id   INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(20) NOT NULL,
    gender       ENUM('男','女'),
    address      VARCHAR(100),
    phone        VARCHAR(20)
);

-- 药品表
CREATE TABLE drug (
    drug_id      INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(50) NOT NULL,
    price        DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock        INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    unit         VARCHAR(10) COMMENT '单位：盒/瓶/支等'
);



-- 用户登录表
CREATE TABLE user (
    user_id      INT PRIMARY KEY AUTO_INCREMENT,
    username     VARCHAR(30) NOT NULL UNIQUE,
    password     VARCHAR(100) NOT NULL,
    role         ENUM('admin','doctor','patient') NOT NULL,
    person_id    INT,
    UNIQUE KEY (role, person_id)
);

-- 门诊挂号表
CREATE TABLE registration (
    reg_id       INT PRIMARY KEY AUTO_INCREMENT,
    patient_id   INT NOT NULL,
    doctor_id    INT NOT NULL,
    reg_time     DATETIME DEFAULT CURRENT_TIMESTAMP,
    status       ENUM('待就诊','已就诊','已缴费','已取消') DEFAULT '待就诊',
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctor(doctor_id)
);

-- 门诊处方表
CREATE TABLE prescription (
    pres_id      INT PRIMARY KEY AUTO_INCREMENT,
    reg_id       INT NOT NULL,
    patient_id   INT NOT NULL,
    doctor_id    INT NOT NULL,
    diagnosis    TEXT COMMENT '症状描述',
    total_fee    DECIMAL(10,2) DEFAULT 0,
    create_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reg_id)     REFERENCES registration(reg_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctor(doctor_id)
);

-- 处方明细表
CREATE TABLE prescription_item (
    item_id      INT PRIMARY KEY AUTO_INCREMENT,
    pres_id      INT NOT NULL,
    drug_id      INT NOT NULL,
    quantity     INT NOT NULL CHECK (quantity > 0),
    price_at_time DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pres_id) REFERENCES prescription(pres_id) ON DELETE CASCADE,
    FOREIGN KEY (drug_id)  REFERENCES drug(drug_id)
);

-- 门诊缴费表
CREATE TABLE payment (
    pay_id       INT PRIMARY KEY AUTO_INCREMENT,
    pres_id      INT NOT NULL UNIQUE,
    amount       DECIMAL(10,2) NOT NULL,
    pay_time     DATETIME DEFAULT CURRENT_TIMESTAMP,
    pay_status   ENUM('未支付','已支付') DEFAULT '未支付',
    FOREIGN KEY (pres_id) REFERENCES prescription(pres_id)
);


-- 病房表
CREATE TABLE ward (
    ward_id      INT PRIMARY KEY AUTO_INCREMENT,
    number       VARCHAR(20) NOT NULL UNIQUE,
    location     VARCHAR(100),
    daily_fee    DECIMAL(10,2) NOT NULL,
    dept_id      INT NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

-- 病床表
CREATE TABLE bed (
    ward_id      INT NOT NULL,
    bed_number   INT NOT NULL,
    PRIMARY KEY (ward_id, bed_number),
    FOREIGN KEY (ward_id) REFERENCES ward(ward_id) ON DELETE CASCADE
);

-- 住院档案表
CREATE TABLE inpatient_archive (
    archive_id   INT PRIMARY KEY AUTO_INCREMENT,
    patient_id   INT NOT NULL,
    ward_id      INT NOT NULL,
    bed_number   INT NOT NULL,
    admit_time   DATETIME DEFAULT CURRENT_TIMESTAMP,
    discharge_time DATETIME,
    deposit      DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (ward_id, bed_number) REFERENCES bed(ward_id, bed_number)
);

-- 住院记录表
CREATE TABLE inpatient_record (
    record_id    INT PRIMARY KEY AUTO_INCREMENT,
    archive_id   INT NOT NULL,
    record_date  DATE NOT NULL,
    symptoms     TEXT,
    treatment    TEXT,
    daily_cost   DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (archive_id) REFERENCES inpatient_archive(archive_id)
);



-- 科室
INSERT INTO department (name, location) VALUES
('内科', '门诊楼2层'),
('外科', '门诊楼3层');

-- 医生
INSERT INTO doctor (name, gender, title, phone, dept_id) VALUES
('张建国', '男', '主任医师', '13800138001', 1),
('李芳', '女', '主治医师', '13800138002', 1),
('王伟', '男', '副主任医师', '13800138003', 2);

-- 病人
INSERT INTO patient (name, gender, address, phone) VALUES
('刘小明', '男', '阳光小区12号', '13912345678'),
('陈丽华', '女', '幸福路8号', '13987654321');

-- 药品
INSERT INTO drug (name, price, stock, unit) VALUES
('阿莫西林胶囊', 25.00, 100, '盒'),
('布洛芬片', 15.00, 200, '瓶'),
('头孢克肟片', 35.00, 80, '盒');

-- 用户账号
INSERT INTO user (username, password, role, person_id) VALUES
('admin', '123456', 'admin', NULL),
('13800138001', '123456', 'doctor', 1),
('13800138002', '123456', 'doctor', 2),
('13800138003', '123456', 'doctor', 3),
('13912345678', '123456', 'patient', 1),
('13987654321', '123456', 'patient', 2);

-- 病房和床位
INSERT INTO ward (number, location, daily_fee, dept_id) VALUES
('101', '住院楼1层', 80.00, 1),
('102', '住院楼1层', 80.00, 1),
('103', '住院楼1层', 100.00, 1),
('201', '住院楼2层', 120.00, 2);

INSERT INTO bed (ward_id, bed_number) VALUES
(1, 1), (1, 2), (1, 3), (1, 4),
(2, 1), (2, 2), (2, 3),
(3, 1), (3, 2), (3, 3),
(4, 1), (4, 2), (4, 3), (4, 4);