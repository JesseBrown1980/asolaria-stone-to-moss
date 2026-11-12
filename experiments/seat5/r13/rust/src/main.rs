#![forbid(unsafe_code)]
use asolaria_seat5_r13::{
    bidirectional_observer, capacity, chariot_walk, decode_flat, encode_flat, encircling_cost_thirds,
    mirror, ordinal, path, synthetic_block, three_way_gate, Encoding, CELLS, CENTER,
};
use std::{env, fs, path::PathBuf};

fn main() {
    let directory = PathBuf::from(env::args().nth(1).expect("usage: seat5-r13 <output-dir>"));
    fs::create_dir_all(&directory).expect("create receipt directory");
    let mut lines = String::new();
    lines.push_str("HBP1|seat=5|round=13|class=COMPUTATIONAL_ADDRESS_ONLY|trits=-1,0,+1|float_used=0\n");
    lines.push_str("SOURCE|combined_books=I-VII|book_of_shadows=NOT_LOCATED|law36=FOUR_POINT_BIDIRECTIONAL|chariots=TWO_AUDIT_SWEEPS\n");
    lines.push_str("MODEL|axis=3x3x3|flat_per_origin=27|free_center_ordinal=13|third=PAID_UNLESS_SUM_CLOSED\n");
    for n in [1u64, 3, 6, 9, 27, 81] {
        let center = 2026i64;
        let samples: Vec<_> = (0..n as i64).map(|i| synthetic_block(center, i)).collect();
        let packed = encode_flat(&samples).expect("encode");
        let (root, paid_offsets) = match &packed {
            Encoding::Shared { observer, blocks_positive } => (*observer, blocks_positive.len() * 13),
            Encoding::Paid(_) => panic!("constructed shared input did not pass"),
        };
        assert_eq!(root, center);
        assert_eq!(decode_flat(&packed).expect("reconstruct"), samples);
        assert_eq!(capacity(n, 3), Ok(n * CELLS as u64));
        lines.push_str(&format!(
            "ADDRESS|origins={n}|cells={}|shared_observer={root}|stored_signed_separations={paid_offsets}|restore=EXACT\n",
            n * CELLS as u64
        ));
    }
    let forward = chariot_walk(true);
    let backward = chariot_walk(false);
    assert_eq!(forward[0], CENTER);
    assert_eq!(backward[0], CENTER);
    for i in 0..CELLS {
        assert_eq!(mirror(forward[i]), Ok(backward[i]));
        assert_eq!(ordinal(path(forward[i]).unwrap()), Ok(forward[i]));
        assert_eq!(ordinal(path(backward[i]).unwrap()), Ok(backward[i]));
    }
    lines.push_str("CHARIOT|forward=COMPLETE27|backward=COMPLETE27|center=SHARED|mirror_pairing=EXACT\n");

    let mut damaged = synthetic_block(2026, 0);
    damaged[0] += 1;
    assert!(matches!(
        encode_flat(&[damaged]),
        Ok(Encoding::Paid(_))
    ));
    let good = synthetic_block(2026, 0);
    let alien = synthetic_block(2027, 0);
    assert!(matches!(
        encode_flat(&[good, alien]),
        Ok(Encoding::Paid(_))
    ));
    assert!(three_way_gate(10, 7, 13, 10));
    assert!(!three_way_gate(10, 7, 13, 11));
    assert_eq!(bidirectional_observer(7, 13), Ok(10));
    assert!(bidirectional_observer(7, 12).is_err());
    lines.push_str("GATE|broken_mirror=PAID|independent_centers=PAID|nonclosing_triad=REJECTED|nonintegral_observer=REJECTED\n");
    assert_eq!(encircling_cost_thirds(27), Ok(135));
    assert_eq!(encircling_cost_thirds(81), Ok(405));
    lines.push_str("THIRDS|units27=135|units81=405|observing_channels27=54|shadow_channels27=27|state_trits_are_not_costs=true\n");
    lines.push_str("BOUNDARY|original_GF2_matrix=UNCHANGED|mod3_cancellation=SEPARATE|no_externally_attested_sensor=TRUE|physical_optical_retention=NOT_TESTED\n");
    let file = directory.join("seat5-r13-center-chariots.hbp");
    fs::write(file, lines.as_bytes()).expect("write canonical HBP");
    print!("{lines}");
}
